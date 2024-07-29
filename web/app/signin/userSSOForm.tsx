'use client'
import { useRouter, useSearchParams } from 'next/navigation'
import type { FC } from 'react'
import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import cn from '@/utils/classnames'
import Toast from '@/app/components/base/toast'
import { getUserOIDCSSOUrl, getUserSAMLSSOUrl } from '@/service/sso'
import Button from '@/app/components/base/button'
import { apiPrefix, ssoProvider } from '@/config'
type UserSSOFormProps = {
  protocol: string
}

const UserSSOForm: FC<UserSSOFormProps> = ({
  protocol,
}) => {
  const searchParams = useSearchParams()
  const consoleToken = searchParams.get('console_token')
  const message = searchParams.get('message')

  const router = useRouter()
  const { t } = useTranslation()

  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    if (consoleToken) {
      localStorage.setItem('console_token', consoleToken)
      router.replace('/apps')
    }

    if (message) {
      Toast.notify({
        type: 'error',
        message,
      })
    }
  }, [])

  const handleSSOLogin = () => {
    setIsLoading(true)
    if (protocol === 'saml') {
      getUserSAMLSSOUrl().then((res) => {
        router.push(res.url)
      }).finally(() => {
        setIsLoading(false)
      })
    }
    else if (protocol === 'oidc') {
      getUserOIDCSSOUrl().then((res) => {
        document.cookie = `user-oidc-state=${res.state}`
        router.push(res.url)
      }).finally(() => {
        setIsLoading(false)
      })
    }
    else if (protocol === 'oauth2') {
      // 跳转到`${apiPrefix}/oauth/login/github`
      router.push(`${apiPrefix}/oauth/login/${ssoProvider}`)
      setIsLoading(false)
    }
    else {
      Toast.notify({
        type: 'error',
        message: 'invalid SSO protocol',
      })
      setIsLoading(false)
    }
  }

  return (
    <div className={
      cn(
        'flex flex-col items-center w-full grow justify-center',
        'px-6',
        'md:px-[108px]',
      )
    }>
      <div className='flex flex-col md:w-[400px]'>
        <div className="w-full mx-auto">
          <h2 className="text-[32px] font-bold text-gray-900">{t('login.pageTitle')}</h2>
        </div>
        <div className="w-full mx-auto mt-10">
          <Button
            tabIndex={0}
            variant='primary'
            onClick={() => { handleSSOLogin() }}
            disabled={isLoading}
            className="w-full"
          >{t('login.sso')}
          </Button>
        </div>
      </div>
    </div>
  )
}

export default UserSSOForm
