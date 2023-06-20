import {Course} from "src/types/Course";

interface Courses {
  username: string
  courses: Course[]

}

export interface MyCoursesResponse {
  success: boolean
  data: Courses
}
