export function formatDateTime(iso) {
  if (!iso) return '-'
  const date = new Date(iso.endsWith('Z') ? iso : `${iso}Z`)
  if (Number.isNaN(date.getTime())) {
    return iso.replace('T', ' ').slice(0, 19)
  }
  return date.toLocaleString('zh-CN', { hour12: false })
}

export function formatDuration(seconds) {
  if (seconds == null || seconds < 0) return '-'
  const minutes = Math.floor(seconds / 60)
  const remainSeconds = seconds % 60
  return `${minutes}分${String(remainSeconds).padStart(2, '0')}秒`
}

export function formatCountdown(seconds) {
  if (seconds == null || seconds < 0) return '00:00'
  const minutes = Math.floor(seconds / 60)
  const remainSeconds = seconds % 60
  return `${String(minutes).padStart(2, '0')}:${String(remainSeconds).padStart(2, '0')}`
}
