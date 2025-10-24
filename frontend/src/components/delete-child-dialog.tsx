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

interface DeleteChildDialogProps {
	childId: string;
	childName: string;
	childEmail: string | null;
	onDelete: (childId: string) => void;
}

export default function DeleteChildDialog({
	childId,
	childName,
	childEmail,
	onDelete,
}: DeleteChildDialogProps) {
	const [open, setOpen] = useState(false);
	const [emailInput, setEmailInput] = useState("");
	const [error, setError] = useState("");
	const emailInputId = useId();

	const handleDelete = () => {
		// メールアドレスが設定されていない場合
		if (!childEmail) {
			setError("このアカウントにはメールアドレスが設定されていません。");
			return;
		}

		// メールアドレスが一致しない場合
		if (emailInput.trim() !== childEmail.trim()) {
			setError("メールアドレスが一致しません。");
			return;
		}

		// 削除実行
		onDelete(childId);
		setOpen(false);
		setEmailInput("");
		setError("");
	};

	const handleOpenChange = (newOpen: boolean) => {
		setOpen(newOpen);
		if (!newOpen) {
			// ダイアログを閉じるときは入力をリセット
			setEmailInput("");
			setError("");
		}
	};

	return (
		<Dialog open={open} onOpenChange={handleOpenChange}>
			<DialogTrigger asChild>
				<Button variant="destructive" className="w-full">
					<Trash2 className="w-4 h-4 mr-2" />
					このアカウントを削除
				</Button>
			</DialogTrigger>
			<DialogContent className="sm:max-w-[500px]">
				<DialogHeader>
					<div className="flex items-center gap-3 mb-2">
						<div className="w-12 h-12 rounded-full bg-red-100 flex items-center justify-center">
							<AlertTriangle className="w-6 h-6 text-red-600" />
						</div>
						<DialogTitle className="text-xl text-red-900">
							アカウントの削除
						</DialogTitle>
					</div>
					<DialogDescription className="text-base">
						<span className="font-semibold text-gray-900">{childName}</span>{" "}
						のアカウントを完全に削除します。
					</DialogDescription>
				</DialogHeader>

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

					{/* メールアドレス表示 */}
					{childEmail ? (
						<div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
							<p className="text-sm text-gray-700 mb-2">
								登録されているメールアドレス：
							</p>
							<p className="text-base font-mono font-semibold text-gray-900">
								{childEmail}
							</p>
						</div>
					) : (
						<div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
							<p className="text-sm text-yellow-800">
								⚠️ このアカウントにはメールアドレスが設定されていません。
								削除を続行できません。
							</p>
						</div>
					)}

					{/* 確認用メールアドレス入力 */}
					{childEmail && (
						<div>
							<Label htmlFor={emailInputId} className="text-base">
								確認のため、上記のメールアドレスを入力してください
							</Label>
							<Input
								id={emailInputId}
								type="email"
								value={emailInput}
								onChange={(e) => {
									setEmailInput(e.target.value);
									setError("");
								}}
								placeholder="メールアドレスを入力"
								className="mt-2"
								autoComplete="off"
							/>
							{error && <p className="text-sm text-red-600 mt-2">{error}</p>}
						</div>
					)}
				</div>

				<DialogFooter>
					<Button variant="outline" onClick={() => handleOpenChange(false)}>
						キャンセル
					</Button>
					<Button
						variant="destructive"
						onClick={handleDelete}
						disabled={!childEmail || !emailInput}
					>
						<Trash2 className="w-4 h-4 mr-2" />
						削除を実行
					</Button>
				</DialogFooter>
			</DialogContent>
		</Dialog>
	);
}
