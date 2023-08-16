export interface GatCourse {
  name: string
  display_name: string
}

export interface GatAutolabCourse extends GatCourse {
  role: string,
  semester: string,
}

export interface GatAutolabCoursesResponse {
  courses: GatAutolabCourse[]
  email: string
}

export interface GatGradingAssignment {
  archived: boolean
  assessment_display_name: string
  assessment_name: string
  course: GatCourse
  created_at: string
  created_by_display_name: string
  created_by_email: string
  id: number
}

export interface GatGradingAssignmentsResponse {
  course: GatCourse
  grading_assignments: GatGradingAssignment[]
}

export interface GatCourseUser {
  display_name: string
  email: string
  grading_hours: number
  is_current_user?: boolean
  is_grader: boolean
  role: string
}

export interface GatCourseUsersResponse {
  course: GatCourse
  current_user_in_graders_roster: boolean
  graders: GatCourseUser[]
  students: GatCourseUser[]
}
