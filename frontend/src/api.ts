const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8787'

export async function requestResearch(
  request: string,
  signal?: AbortSignal,
): Promise<string> {
  const response = await fetch(`${API_BASE_URL}/api/research`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ request }),
    signal,
  })

  if (!response.ok) {
    const text = await response.text()
    throw new Error(text || `Research request failed with ${response.status}`)
  }

  const payload: unknown = await response.json()

  if (
    !payload ||
    typeof payload !== 'object' ||
    !('answer' in payload) ||
    typeof payload.answer !== 'string'
  ) {
    throw new Error('Research response did not include an answer.')
  }

  return payload.answer
}

export type UploadResult = {
  uploaded: Array<{ name: string; size: number; type: string }>
}

export async function uploadSources(files: FileList): Promise<UploadResult> {
  const formData = new FormData()

  for (let i = 0; i < files.length; i++) {
    const file = files.item(i)

    if (file) {
      formData.append('files', file)
    }
  }

  const response = await fetch(`${API_BASE_URL}/api/sources`, {
    method: 'POST',
    body: formData,
  })

  if (!response.ok) {
    const text = await response.text()
    throw new Error(text || `Source upload failed with ${response.status}`)
  }

  return (await response.json()) as UploadResult
}
