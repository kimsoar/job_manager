import { watch } from 'vue'

export function useScreen(onChange?: (newVal: ScreenType, oldVal: ScreenType) => void) {
  const isSm = useMediaQuery('(max-width: 767px)')
  const isMd = useMediaQuery('(min-width: 768px) and (max-width: 1023px)')
  const isLg = useMediaQuery('(min-width: 1024px)')

  const screenType = computed<ScreenType>(() => {
    if (isSm.value) return 'sm'
    if (isMd.value) return 'md'
    return 'lg'
  })

  if (onChange) {
    watch(screenType, (n, o) => {
      if (!o) return
      onChange(n, o)
    })
  }

  return { screenType }
}
