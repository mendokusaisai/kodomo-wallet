import {
	GoogleAuthProvider,
	createUserWithEmailAndPassword,
	onAuthStateChanged,
	signInWithEmailAndPassword,
	signInWithPopup,
	signOut as firebaseSignOut,
	type User,
} from "firebase/auth";
import { auth } from "./client";

const SESSION_COOKIE = "__session";
const SESSION_MAX_AGE = 60 * 60 * 24; // 24時間

function setSessionCookie() {
	if (typeof document !== "undefined") {
		document.cookie = `${SESSION_COOKIE}=1; path=/; max-age=${SESSION_MAX_AGE}; SameSite=Lax`;
	}
}

function clearSessionCookie() {
	if (typeof document !== "undefined") {
		document.cookie = `${SESSION_COOKIE}=; path=/; max-age=0`;
	}
}

export async function signIn(email: string, password: string) {
	const credential = await signInWithEmailAndPassword(auth, email, password);
	setSessionCookie();
	return credential;
}

export async function signUp(email: string, password: string) {
	const credential = await createUserWithEmailAndPassword(
		auth,
		email,
		password,
	);
	setSessionCookie();
	return credential;
}

export async function signOut() {
	await firebaseSignOut(auth);
	clearSessionCookie();
}

/**
 * Firebase Auth の初期化完了を待ってから現在のユーザーを返す
 */
export function getUser(): Promise<User | null> {
	return new Promise((resolve) => {
		const unsubscribe = onAuthStateChanged(auth, (user) => {
			unsubscribe();
			resolve(user);
		});
	});
}

/**
 * Firebase ID トークンを取得する（自動リフレッシュ対応）
 */
export async function getIdToken(): Promise<string | null> {
	const user = await getUser();
	if (!user) return null;
	return user.getIdToken();
}

export async function signInWithGoogle() {
	const provider = new GoogleAuthProvider();
	const credential = await signInWithPopup(auth, provider);
	setSessionCookie();
	return credential;
}
