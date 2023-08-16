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
