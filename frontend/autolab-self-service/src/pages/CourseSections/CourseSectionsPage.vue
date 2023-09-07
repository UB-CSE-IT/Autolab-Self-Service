<template>
  <q-page class="q-px-lg q-mx-auto" style="max-width: 1000px;">
    <div class="button-row q-my-lg">
      <q-btn icon="west" label="Back to courses" color="primary" :to="{name: 'course-sections'}"/>
    </div>
    <h4>Manage Course Sections in {{ courseName }}</h4>
    <ApiFetchContentContainer :api-data-loader="courseSectionsLoader" loading-text="Loading course sections">
      <h5>Lectures</h5>
      <CourseSectionsTable v-model="lectureSections" type-name="lecture"/>

      <h5>Sections</h5>
      <CourseSectionsTable v-model="sectionSections" type-name="section"/>

      <DebugBox>
        <pre>{{ courseSectionsLoader.state.data }}</pre>
      </DebugBox>

    </ApiFetchContentContainer>

    <div style="height: 100px;"></div>
  </q-page>
</template>

<script setup lang="ts">
import {useRoute} from 'vue-router'
import {PortalApiDataLoader} from 'src/utilities/PortalApiDataLoader'
import {CourseSectionsResponse} from 'src/types/CourseSectionsTypes'
import ApiFetchContentContainer from 'components/ApiFetchContentContainer.vue'
import CourseSectionsTable from 'components/CourseSections/CourseSectionsTable.vue'
import {computed} from 'vue'
import DebugBox from 'components/Boxes/DebugBox.vue'

const courseName = useRoute().params.courseName
const courseSectionsLoader = new PortalApiDataLoader<CourseSectionsResponse>(`/portal/api/course_sections/${courseName}/`)
courseSectionsLoader.fetch()

const lectureSections = computed(() => courseSectionsLoader.state.data?.sections.filter(section => section.is_lecture))
const sectionSections = computed(() => courseSectionsLoader.state.data?.sections.filter(section => !section.is_lecture))

</script>
