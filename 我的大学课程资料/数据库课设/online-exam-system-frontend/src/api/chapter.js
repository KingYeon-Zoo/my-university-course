import request from '@/utils/request'

export function listChapter(courseId) {
  return request({
    url: 'chapter/list',
    method: 'get',
    params: { courseId }
  })
}

export function addChapter(data) {
  return request({
    url: 'chapter',
    method: 'post',
    data
  })
}

export function updateChapter(id, data) {
  return request({
    url: `chapter/${id}`,
    method: 'put',
    data
  })
}

export function deleteChapter(id) {
  return request({
    url: `chapter/${id}`,
    method: 'delete'
  })
}
