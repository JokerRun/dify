'use client'

import { SWRConfig } from 'swr'
import { useEffect, useState } from 'react'
import type { ReactNode } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { apiPrefix, ssoProvider } from '@/config'

type SwrInitorProps = {
  children: ReactNode
}
const SwrInitor = ({
  children,
}: SwrInitorProps) => {
  const router = useRouter()
  const searchParams = useSearchParams()
  const consoleToken = searchParams.get('console_token')
  const consoleTokenFromLocalStorage = localStorage?.getItem('console_token')
  const [init, setInit] = useState(false)

  useEffect(() => {
    if (!(consoleToken || consoleTokenFromLocalStorage))
      router.push(`${apiPrefix}/oauth/login/${ssoProvider}`)

    if (consoleToken) {
      localStorage?.setItem('console_token', consoleToken!)
      const redirectUrl = localStorage.getItem('redirect_url')
      if (redirectUrl) {
        window.location.href = redirectUrl
        // 可选：重定向后清除 localStorage 中的 redirect_url
        localStorage.removeItem('redirect_url')
      }
      else {
        router.replace('/apps', { forceOptimisticNavigation: false } as any)
      }
    }
    setInit(true)
  }, [])

  return init
    ? (
      <SWRConfig value={{
        shouldRetryOnError: false,
        revalidateOnFocus: false,
      }}>
        {children}
      </SWRConfig>
    )
    : null
}

export default SwrInitor
