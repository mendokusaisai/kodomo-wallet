"use client";

import { useMutation, useQuery } from "@apollo/client/react";
import { format, parseISO } from "date-fns";
import { ja } from "date-fns/locale";
import { CheckCircle, Clock, XCircle } from "lucide-react";
import { ConfirmDialog } from "@/components/confirm-dialog";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import {
	APPROVE_WITHDRAWAL,
	GET_WITHDRAWAL_REQUESTS,
	REJECT_WITHDRAWAL,
} from "@/lib/graphql/queries";
import { showError, showSuccess } from "@/lib/toast";

interface WithdrawalRequest {
	id: string;
	accountId: string;
	amount: number;
	description: string | null;
	status: string;
	createdAt: string;
	updatedAt: string;
}

interface GetWithdrawalRequestsResponse {
	withdrawalRequests: WithdrawalRequest[];
}

interface WithdrawalRequestsListProps {
	parentId: string;
}

export default function WithdrawalRequestsList({
	parentId,
}: WithdrawalRequestsListProps) {
	const { data, loading, refetch } = useQuery<GetWithdrawalRequestsResponse>(
		GET_WITHDRAWAL_REQUESTS,
		{
			variables: { parentId },
		},
	);

	const [approveWithdrawal] = useMutation(APPROVE_WITHDRAWAL, {
		refetchQueries: ["GetAccounts", "GetTransactions", "GetWithdrawalRequests"],
		onCompleted: () => {
			showSuccess("出金申請を承認しました");
			refetch();
		},
		onError: (error: { message: string }) => {
			showError("承認に失敗しました", error.message);
		},
	});

	const [rejectWithdrawal] = useMutation(REJECT_WITHDRAWAL, {
		refetchQueries: ["GetWithdrawalRequests"],
		onCompleted: () => {
			showSuccess("出金申請を却下しました");
			refetch();
		},
		onError: (error: { message: string }) => {
			showError("却下に失敗しました", error.message);
		},
	});

	const handleApprove = async (requestId: string) => {
		await approveWithdrawal({ variables: { requestId } });
	};

	const handleReject = async (requestId: string) => {
		await rejectWithdrawal({ variables: { requestId } });
	};

	if (loading) {
		return (
			<div className="space-y-4">
				{[1, 2, 3].map((i) => (
					<Skeleton key={i} className="h-24 w-full" />
				))}
			</div>
		);
	}

	const requests: WithdrawalRequest[] = data?.withdrawalRequests || [];

	if (requests.length === 0) {
		return (
			<div className="text-center py-8 text-gray-500 dark:text-gray-400 bg-gray-50 dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
				出金申請はありません
			</div>
		);
	}

	return (
		<div className="space-y-4">
			{requests.map((request: WithdrawalRequest) => (
				<div
					key={request.id}
					className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 bg-white dark:bg-gray-900 shadow-sm"
				>
					<div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
						<div className="flex-1 min-w-0">
							<div className="flex items-center gap-2">
								<Clock className="w-4 h-4 text-yellow-600 dark:text-yellow-500 flex-shrink-0" />
								<span className="font-semibold text-gray-900 dark:text-gray-100">
									¥{request.amount.toLocaleString()}
								</span>
							</div>
							<p className="text-sm text-gray-600 dark:text-gray-400 mt-1 truncate">
								{request.description || "（メモなし）"}
							</p>
							<p className="text-xs text-gray-400 dark:text-gray-500 mt-1">
								申請日:{" "}
								{format(parseISO(request.createdAt), "M月d日 HH:mm", {
									locale: ja,
								})}
							</p>
						</div>
						<div className="flex gap-2 w-full sm:w-auto">
							<ConfirmDialog
								trigger={
									<Button
										size="sm"
										variant="outline"
										className="border-green-600 text-green-600 hover:bg-green-50 dark:hover:bg-green-950 flex-1 sm:flex-none"
									>
										<CheckCircle className="w-4 h-4 mr-1" />
										承認
									</Button>
								}
								title="出金申請を承認"
								description="この出金申請を承認しますか？承認すると、子どものアカウントから出金されます。"
								confirmText="承認する"
								onConfirm={() => handleApprove(request.id)}
							/>
							<ConfirmDialog
								trigger={
									<Button
										size="sm"
										variant="outline"
										className="border-red-600 text-red-600 hover:bg-red-50 dark:hover:bg-red-950 flex-1 sm:flex-none"
									>
										<XCircle className="w-4 h-4 mr-1" />
										却下
									</Button>
								}
								title="出金申請を却下"
								description="この出金申請を却下しますか？"
								confirmText="却下する"
								variant="destructive"
								onConfirm={() => handleReject(request.id)}
							/>
						</div>
					</div>
				</div>
			))}
		</div>
	);
}
