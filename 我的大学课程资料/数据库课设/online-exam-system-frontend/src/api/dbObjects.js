import request from '@/utils/request'

export function getCourseStats(courseId) {
  return request({
    url: `db-objects/course-stats/${courseId}`,
    method: 'get'
  })
}

export function getAllCoursesStats() {
  return request({
    url: 'db-objects/all-courses-stats',
    method: 'get'
  })
}

export function getCourseTypesFromView() {
  return request({
    url: 'db-objects/view/course-types',
    method: 'get'
  })
}

export function autoAssemblePaper(data) {
  return request({
    url: 'db-objects/auto-assemble',
    method: 'post',
    data
  })
}
