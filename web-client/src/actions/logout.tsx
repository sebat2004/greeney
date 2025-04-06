import { signOut } from '@/lib/auth';

export default async function login() {
    return await signOut();
}
