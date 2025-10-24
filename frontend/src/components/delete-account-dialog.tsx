"use client";

import { AlertTriangle, Trash2 } from "lucide-react";
import { useId, useState } from "react";
import { Button } from "@/components/ui/button";
import {
	Dialog,
	DialogContent,
	DialogDescription,
	DialogFooter,
	DialogHeader,
	DialogTitle,
	DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

interface DeleteAccountDialogProps {
	accountId: string;
	accountName: string;
	onDelete: (accountId: string) => void;
	buttonText?: string;
	title?: string;
	description?: React.ReactNode;
	triggerButton?: React.ReactNode;
}

export default function DeleteAccountDialog({
	accountId,
	accountName,
	onDelete,
	buttonText = "このアカウントを削除",
	title = "アカウントの削除",
	description,
	triggerButton,
}: DeleteAccountDialogProps) {
	const [open, setOpen] = useState(false);
	const [nameInput, setNameInput] = useState("");
	const [error, setError] = useState("");
	const nameInputId = useId();

	const handleDelete = () => {
		// ユーザー名が一致しない場合
		if (nameInput.trim() !== accountName.trim()) {
			setError("ユーザー名が一致しません。");
			return;
		}

		// 削除実行
		onDelete(accountId);
		setOpen(false);
		setNameInput("");
		setError("");
	};

	const handleOpenChange = (newOpen: boolean) => {
		setOpen(newOpen);
		if (!newOpen) {
			// ダイアログを閉じるときは入力をリセット
			setNameInput("");
			setError("");
		}
	};

	return (
		<Dialog open={open} onOpenChange={handleOpenChange}>
			<DialogTrigger asChild>
				{triggerButton || (
					<Button variant="destructive" className="w-full">
						<Trash2 className="w-4 h-4 mr-2" />
						{buttonText}
					</Button>
				)}
			</DialogTrigger>
			<DialogContent className="sm:max-w-[500px]">
				<DialogHeader>
					<div className="flex items-center gap-3 mb-2">
						<div className="w-12 h-12 rounded-full bg-red-100 flex items-center justify-center">
							<AlertTriangle className="w-6 h-6 text-red-600" />
						</div>
						<DialogTitle className="text-xl text-red-900">{title}</DialogTitle>
					</div>
					<DialogDescription className="text-base">
						{description || (
							<span>
								<span className="font-semibold text-gray-900">
									{accountName}
								</span>{" "}
								のアカウントを完全に削除します。
							</span>
						)}
					</DialogDescription>
				</DialogHeader>{" "}
				<div className="space-y-4 py-4">
					{/* 警告メッセージ */}
					<div className="bg-red-50 border border-red-200 rounded-lg p-4">
						<p className="text-sm text-red-800 font-semibold mb-2">
							⚠️ この操作は取り消せません
						</p>
						<p className="text-sm text-red-700">削除されるデータ：</p>
						<ul className="text-sm text-red-700 list-disc list-inside mt-1 space-y-1">
							<li>残高情報</li>
							<li>トランザクション履歴</li>
							<li>貯金目標</li>
							<li>出金リクエスト</li>
							<li>すべてのアカウントデータ</li>
						</ul>
					</div>

					{/* ユーザー名表示 */}
					<div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
						<p className="text-sm text-gray-700 mb-2">削除対象のユーザー名：</p>
						<p className="text-base font-semibold text-gray-900">
							{accountName}
						</p>
					</div>

					{/* 確認用ユーザー名入力 */}
					<div>
						<Label htmlFor={nameInputId} className="text-base">
							確認のため、上記のユーザー名を入力してください
						</Label>
						<Input
							id={nameInputId}
							type="text"
							value={nameInput}
							onChange={(e) => {
								setNameInput(e.target.value);
								setError("");
							}}
							placeholder="ユーザー名を入力"
							className="mt-2"
							autoComplete="off"
						/>
						{error && <p className="text-sm text-red-600 mt-2">{error}</p>}
					</div>
				</div>
				<DialogFooter>
					<Button variant="outline" onClick={() => handleOpenChange(false)}>
						キャンセル
					</Button>
					<Button
						variant="destructive"
						onClick={handleDelete}
						disabled={!nameInput}
					>
						<Trash2 className="w-4 h-4 mr-2" />
						削除を実行
					</Button>
				</DialogFooter>
			</DialogContent>
		</Dialog>
	);
}
