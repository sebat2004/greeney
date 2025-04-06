import { signIn } from '@/lib/auth';

export default async function login() {
    return await signIn('google');
}
