"use client";

import type { ReactElement, ReactNode } from "react";
import { cloneElement, isValidElement, useState } from "react";
import { Button } from "@/components/ui/button";
import {
	Dialog,
	DialogContent,
	DialogDescription,
	DialogFooter,
	DialogHeader,
	DialogTitle,
} from "@/components/ui/dialog";

interface TriggerProps {
	onClick?: (e: React.MouseEvent) => void;
	[key: string]: unknown;
}

interface ConfirmDialogProps {
	trigger: ReactNode;
	title: string;
	description: string;
	confirmText?: string;
	cancelText?: string;
	variant?: "default" | "destructive";
	onConfirm: () => void | Promise<void>;
}

export function ConfirmDialog({
	trigger,
	title,
	description,
	confirmText = "確認",
	cancelText = "キャンセル",
	variant = "default",
	onConfirm,
}: ConfirmDialogProps) {
	const [open, setOpen] = useState(false);
	const [loading, setLoading] = useState(false);

	const handleConfirm = async () => {
		setLoading(true);
		try {
			await onConfirm();
			setOpen(false);
		} catch (error) {
			console.error("確認アクションエラー:", error);
		} finally {
			setLoading(false);
		}
	};

	// triggerにonClickハンドラを追加
	const triggerElement = isValidElement(trigger)
		? cloneElement(trigger as ReactElement<TriggerProps>, {
				onClick: (e: React.MouseEvent) => {
					e.preventDefault();
					// 元のonClickがあれば実行
					const originalOnClick = (trigger as ReactElement<TriggerProps>).props
						.onClick;
					if (originalOnClick) {
						originalOnClick(e);
					}
					setOpen(true);
				},
			})
		: trigger;

	return (
		<Dialog open={open} onOpenChange={setOpen}>
			{triggerElement}
			<DialogContent>
				<DialogHeader>
					<DialogTitle>{title}</DialogTitle>
					<DialogDescription>{description}</DialogDescription>
				</DialogHeader>
				<DialogFooter className="gap-2">
					<Button
						variant="outline"
						onClick={() => setOpen(false)}
						disabled={loading}
					>
						{cancelText}
					</Button>
					<Button variant={variant} onClick={handleConfirm} disabled={loading}>
						{loading ? "処理中..." : confirmText}
					</Button>
				</DialogFooter>
			</DialogContent>
		</Dialog>
	);
}
