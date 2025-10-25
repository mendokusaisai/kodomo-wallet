"use client";

import { motion } from "framer-motion";
import type { ReactNode } from "react";

interface FadeInProps {
	children: ReactNode;
	delay?: number;
	className?: string;
}

/**
 * フェードインアニメーション
 */
export function FadeIn({ children, delay = 0, className }: FadeInProps) {
	return (
		<motion.div
			initial={{ opacity: 0, y: 20 }}
			animate={{ opacity: 1, y: 0 }}
			transition={{ duration: 0.4, delay }}
			className={className}
		>
			{children}
		</motion.div>
	);
}

interface SlideInProps {
	children: ReactNode;
	direction?: "left" | "right" | "up" | "down";
	delay?: number;
	className?: string;
}

/**
 * スライドインアニメーション
 */
export function SlideIn({
	children,
	direction = "up",
	delay = 0,
	className,
}: SlideInProps) {
	const directions = {
		left: { x: -50, y: 0 },
		right: { x: 50, y: 0 },
		up: { x: 0, y: 20 },
		down: { x: 0, y: -20 },
	};

	return (
		<motion.div
			initial={{ opacity: 0, ...directions[direction] }}
			animate={{ opacity: 1, x: 0, y: 0 }}
			transition={{ duration: 0.5, delay }}
			className={className}
		>
			{children}
		</motion.div>
	);
}

interface ScaleInProps {
	children: ReactNode;
	delay?: number;
	className?: string;
}

/**
 * スケールインアニメーション
 */
export function ScaleIn({ children, delay = 0, className }: ScaleInProps) {
	return (
		<motion.div
			initial={{ opacity: 0, scale: 0.9 }}
			animate={{ opacity: 1, scale: 1 }}
			transition={{ duration: 0.3, delay }}
			className={className}
		>
			{children}
		</motion.div>
	);
}

interface StaggerContainerProps {
	children: ReactNode;
	className?: string;
}

/**
 * 子要素を順次アニメーションさせるコンテナ
 */
export function StaggerContainer({
	children,
	className,
}: StaggerContainerProps) {
	return (
		<motion.div
			initial="hidden"
			animate="visible"
			variants={{
				visible: {
					transition: {
						staggerChildren: 0.1,
					},
				},
			}}
			className={className}
		>
			{children}
		</motion.div>
	);
}

interface StaggerItemProps {
	children: ReactNode;
	className?: string;
}

/**
 * StaggerContainer内で使用する子要素
 */
export function StaggerItem({ children, className }: StaggerItemProps) {
	return (
		<motion.div
			variants={{
				hidden: { opacity: 0, y: 20 },
				visible: { opacity: 1, y: 0 },
			}}
			transition={{ duration: 0.4 }}
			className={className}
		>
			{children}
		</motion.div>
	);
}
