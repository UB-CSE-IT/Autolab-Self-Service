import {RouteRecordRaw} from 'vue-router';

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      {
        path: '',
        component: () => import('pages/IndexPage.vue')
      },
      {
        path: 'create-course',
        name: 'create-course',
        component: () => import('pages/CreateCoursePage.vue')
      },
      {
        path: 'become-admin',
        name: 'become-admin',
        component: () => import('pages/BecomeAdminPage.vue')
      },
      {
        path: 'tango-statistics',
        name: 'tango-statistics',
        component: () => import('pages/TangoStatsPage.vue')
      },
      // Always leave this as last one,
      // but you can also remove it
      {
        path: '/:catchAll(.*)*',
        component: () => import('pages/ErrorNotFound.vue'),
      },
    ],
  },


];

export default routes;
