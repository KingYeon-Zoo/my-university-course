import request from '@/utils/request'

export function listQuestionType() {
  return request({
    url: 'question-type/list',
    method: 'get'
  })
}

export function getTypesByCourse(courseId) {
  return request({
    url: `question-type/course/${courseId}`,
    method: 'get'
  })
}

export function updateCourseTypes(courseId, typeIds) {
  return request({
    url: `question-type/course/${courseId}`,
    method: 'post',
    data: typeIds
  })
}
