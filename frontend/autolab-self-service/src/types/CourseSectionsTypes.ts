import {GatAutolabCourse} from 'src/types/GradingAssignmentToolTypes'

export interface CourseSection {
  name: string
  is_lecture: boolean
  start_time: string
  end_time: string
  days_code: number
  updated?: boolean
}
export interface CourseSectionsResponse {
  course: GatAutolabCourse
  sections: CourseSection[]
}
