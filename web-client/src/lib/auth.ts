import NextAuth, { type DefaultSession } from 'next-auth';
import Google from 'next-auth/providers/google';

declare module 'next-auth' {
    interface Session {
        accessToken: string;
        user: {
            id: string;
        } & DefaultSession['user'];
    }

    interface JWT {
        accessToken?: string;
    }
}

export const { handlers, signIn, signOut, auth } = NextAuth({
    providers: [
        Google({
            authorization: {
                params: {
                    prompt: 'consent',
                    access_type: 'offline',
                    response_type: 'code',
                    scope: 'openid email profile https://www.googleapis.com/auth/gmail.readonly',
                },
            },
        }),
    ],
    callbacks: {
        async jwt({ token, account }) {
            // account is only available on first sign-in
            if (account) {
                token.accessToken = account.access_token;
            }
            return token;
        },
        async session({ session, token }) {
            if (token && token.sub) {
                session.user.id = token.sub;
            }
            if (token.accessToken) {
                session.accessToken = token.accessToken as string;
            }
            return session;
        },
    },
});
