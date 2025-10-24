import { createClient } from "./client";

export async function signUp(email: string, password: string, name: string) {
	const supabase = createClient();

	const { data, error } = await supabase.auth.signUp({
		email,
		password,
		options: {
			data: {
				name,
			},
		},
	});

	if (error) throw error;
	return data;
}

export async function signIn(email: string, password: string) {
	const supabase = createClient();

	const { data, error } = await supabase.auth.signInWithPassword({
		email,
		password,
	});

	if (error) throw error;
	return data;
}

export async function signOut() {
	const supabase = createClient();

	const { error } = await supabase.auth.signOut();

	if (error) throw error;
}

export async function getSession() {
	const supabase = createClient();

	const { data, error } = await supabase.auth.getSession();

	if (error) throw error;
	return data.session;
}

export async function getUser() {
	const supabase = createClient();

	const { data, error } = await supabase.auth.getUser();

	if (error) throw error;
	return data.user;
}
