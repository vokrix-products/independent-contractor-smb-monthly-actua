import { createFileRoute, useNavigate } from '@tanstack/react-router'
import { useEffect } from 'react'
import { supabase } from '@/lib/supabase'

export const Route = createFileRoute('/(auth)/auth-callback')({
  component: AuthCallback,
})

function AuthCallback() {
  const navigate = useNavigate()
  useEffect(() => {
    async function handleCallback() {
      // Handle OTP magic link: ?token_hash=...&type=email
      const searchParams = new URLSearchParams(window.location.search)
      const token_hash = searchParams.get('token_hash')
      const type = searchParams.get('type')

      if (token_hash && type) {
        const { error } = await supabase.auth.verifyOtp({ token_hash, type: type as 'email' })
        if (!error) { navigate({ to: '/' }); return }
      }

      // Handle OAuth hash: #access_token=...&refresh_token=...
      const hash = window.location.hash.slice(1)
      const params = new URLSearchParams(hash)
      const access_token = params.get('access_token')
      const refresh_token = params.get('refresh_token')

      if (access_token && refresh_token) {
        const { data } = await supabase.auth.setSession({ access_token, refresh_token })
        if (data.session) { navigate({ to: '/' }); return }
      }

      navigate({ to: '/sign-up' })
    }
    void handleCallback()
  }, [navigate])

  return (
    <div className='flex h-screen items-center justify-center'>
      <p className='text-muted-foreground'>Signing you in...</p>
    </div>
  )
}
