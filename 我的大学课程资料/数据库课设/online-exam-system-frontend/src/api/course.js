import request from '@/utils/request'

export function listCourse() {
  return request({
    url: 'course/list',
    method: 'get'
  })
}

export function addCourse(data) {
  return request({
    url: 'course',
    method: 'post',
    data
  })
}

export function updateCourse(id, data) {
  return request({
    url: `course/${id}`,
    method: 'put',
    data
  })
}

export function deleteCourse(id) {
  return request({
    url: `course/${id}`,
    method: 'delete'
  })
}
