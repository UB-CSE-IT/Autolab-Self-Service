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

export interface GatCoursePersonResponse {
  conflicts_of_interest: string[] // Array of email addresses
  course: GatCourse
  user: GatCourseUser
}

export interface GatConflictOfInterestResponse {
  grader_email: string
  student_email: string
}

export interface GatAutolabAssessment {
  display_name: string
  name: string
  url: string
}

export interface GatAutolabAssessmentsResponse {
  assessments: GatAutolabAssessment[]
  course: GatCourse
}


export interface GatCreateGradingAssignmentResponse {
  id: number
  grading_assignment: GatGradingAssignment
}

export interface GatGrader {
  display_name: string
  email: string
  is_current_user: boolean
}

export interface GatGradingAssignmentPairSubmission {
  completed: boolean
  pair_id: number
  student_display_name: string
  student_email: string
  submission_url: string
  submission_version: number
}

export interface GatGraderSubmissions {
  grader: GatGrader
  submissions: GatGradingAssignmentPairSubmission[]
}

export interface GatGradingAssignmentResponse {
  grading_assignment: GatGradingAssignment
  grading_assignment_pairs: GatGraderSubmissions[]
}
