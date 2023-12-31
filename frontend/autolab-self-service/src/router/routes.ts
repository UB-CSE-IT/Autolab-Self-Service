import {RouteRecordRaw} from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      {
        path: '',
        name: 'index',
        component: () => import('pages/IndexPage.vue'),
      },
      {
        path: 'create-course',
        name: 'create-course',
        component: () => import('pages/CreateCoursePage.vue'),
      },
      {
        path: 'become-admin',
        name: 'become-admin',
        component: () => import('pages/BecomeAdminPage.vue'),
      },
      {
        path: 'tango-statistics',
        name: 'tango-statistics',
        component: () => import('pages/TangoStatsPage.vue'),
      },
      {
        path: 'gat',
        children: [
          {
            path: '',
            name: 'grader-assignment-tool',
            component: () => import('pages/GraderAssignmentTool/CourseListPage.vue'),
          },
          {
            path: ':courseName',
            name: 'grader-assignment-tool-course',
            component: () => import('pages/GraderAssignmentTool/CoursePage.vue'),
          },
          {
            path: ':courseName/people',
            name: 'grader-assignment-tool-people',
            component: () => import('pages/GraderAssignmentTool/PeoplePage.vue'),
          },
          {
            path: ':courseName/people/:user/', // The trailing slash is required for the . in the email address
            name: 'grader-assignment-tool-person',
            component: () => import('pages/GraderAssignmentTool/PersonPage.vue'),
          },
          {
            path: ':courseName/assignments/new',
            name: 'grader-assignment-tool-autolab-assessments',
            component: () => import('pages/GraderAssignmentTool/AutolabAssessmentsPage.vue'),
          },
          {
            path: ':courseName/assignments/new/:assessmentName',
            name: 'grader-assignment-tool-create-new-assignment',
            component: () => import('pages/GraderAssignmentTool/CreateNewGradingAssignmentPage.vue'),
          },
          {
            path: ':courseName/assignments/:assignmentId',
            name: 'grader-assignment-tool-assignment',
            component: () => import('pages/GraderAssignmentTool/GradingAssignmentPage.vue'),
          },
        ],
      },
      {
        path: 'course-sections',
        name: 'course-sections',
        component: () => import('pages/CourseSections/CourseListPage.vue'),
      },
      {
        path: 'course-sections/:courseName',
        name: 'course-sections-course',
        component: () => import('pages/CourseSections/CourseSectionsPage.vue'),
      },

      // Always leave this as last one,
      // but you can also remove it
      {
        path: '/:catchAll(.*)*',
        component: () => import('pages/ErrorNotFound.vue'),
      },
    ],
  },


]

export default routes
