"use client";

import { useMutation, useQuery } from "@apollo/client/react";
import { format, parseISO } from "date-fns";
import { ja } from "date-fns/locale";
import { CheckCircle, Clock, XCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
	APPROVE_WITHDRAWAL,
	GET_WITHDRAWAL_REQUESTS,
	REJECT_WITHDRAWAL,
} from "@/lib/graphql/queries";

interface WithdrawalRequest {
	id: string;
	accountId: string;
	amount: number;
	description: string | null;
	status: string;
	createdAt: string;
	updatedAt: string;
}

interface WithdrawalRequestsListProps {
	parentId: string;
}

export default function WithdrawalRequestsList({
	parentId,
}: WithdrawalRequestsListProps) {
	const { data, loading, refetch } = useQuery(GET_WITHDRAWAL_REQUESTS, {
		variables: { parentId },
	});

	const [approveWithdrawal] = useMutation(APPROVE_WITHDRAWAL, {
		refetchQueries: ["GetAccounts", "GetTransactions", "GetWithdrawalRequests"],
		onCompleted: () => {
			refetch();
		},
		onError: (error: { message: string }) => {
			alert(`承認に失敗しました: ${error.message}`);
		},
	});

	const [rejectWithdrawal] = useMutation(REJECT_WITHDRAWAL, {
		refetchQueries: ["GetWithdrawalRequests"],
		onCompleted: () => {
			refetch();
		},
		onError: (error: { message: string }) => {
			alert(`却下に失敗しました: ${error.message}`);
		},
	});

	const handleApprove = async (requestId: string) => {
		if (
			confirm(
				"この出金申請を承認しますか？承認すると、子どものアカウントから出金されます。",
			)
		) {
			await approveWithdrawal({ variables: { requestId } });
		}
	};

	const handleReject = async (requestId: string) => {
		if (confirm("この出金申請を却下しますか？")) {
			await rejectWithdrawal({ variables: { requestId } });
		}
	};

	if (loading) {
		return (
			<div className="flex justify-center py-8">
				<div className="animate-spin h-8 w-8 border-4 border-blue-500 border-t-transparent rounded-full"></div>
			</div>
		);
	}

	const requests: WithdrawalRequest[] = data?.withdrawalRequests || [];

	if (requests.length === 0) {
		return (
			<div className="text-center py-8 text-gray-500">出金申請はありません</div>
		);
	}

	return (
		<div className="space-y-4">
			{requests.map((request: WithdrawalRequest) => (
				<div
					key={request.id}
					className="border rounded-lg p-4 bg-white shadow-sm"
				>
					<div className="flex items-center justify-between">
						<div className="flex-1">
							<div className="flex items-center gap-2">
								<Clock className="w-4 h-4 text-yellow-600" />
								<span className="font-semibold text-gray-900">
									¥{request.amount.toLocaleString()}
								</span>
							</div>
							<p className="text-sm text-gray-600 mt-1">
								{request.description || "（メモなし）"}
							</p>
							<p className="text-xs text-gray-400 mt-1">
								申請日:{" "}
								{format(parseISO(request.createdAt), "M月d日 HH:mm", {
									locale: ja,
								})}
							</p>
						</div>
						<div className="flex gap-2">
							<Button
								size="sm"
								variant="outline"
								className="border-green-600 text-green-600 hover:bg-green-50"
								onClick={() => handleApprove(request.id)}
							>
								<CheckCircle className="w-4 h-4 mr-1" />
								承認
							</Button>
							<Button
								size="sm"
								variant="outline"
								className="border-red-600 text-red-600 hover:bg-red-50"
								onClick={() => handleReject(request.id)}
							>
								<XCircle className="w-4 h-4 mr-1" />
								却下
							</Button>
						</div>
					</div>
				</div>
			))}
		</div>
	);
}
