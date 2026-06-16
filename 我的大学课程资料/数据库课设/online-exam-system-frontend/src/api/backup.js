import request from '@/utils/request'

export function triggerBackup() {
  return request({
    url: 'backup',
    method: 'post'
  })
}

export function listBackup() {
  return request({
    url: 'backup/list',
    method: 'get'
  })
}

export function triggerRestore(fileName) {
  return request({
    url: 'backup/restore',
    method: 'post',
    params: { fileName }
  })
}

export function deleteBackup(fileName) {
  return request({
    url: `backup/${fileName}`,
    method: 'delete'
  })
}
