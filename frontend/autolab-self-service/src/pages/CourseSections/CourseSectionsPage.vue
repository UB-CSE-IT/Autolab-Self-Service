<template>
  <q-page class="q-px-lg q-mx-auto" style="max-width: 1000px;">
    <div class="button-row q-my-lg">
      <q-btn icon="west" label="Back to courses" color="primary" :to="{name: 'course-sections'}"/>
    </div>
    <h4>Manage Course Sections in {{ courseName }}</h4>

    <div class="button-row q-my-lg" v-if="courseSectionsLoader.state.loaded">
      <q-btn label="Save"
             color="primary"
             icon="save"
             @click="updateSections"
             :loading="courseSectionsSubmitter.state.loading"
             :disable="!unsavedChanges"/>
      <q-btn label="Magic Import"
             color="primary"
             icon="sync"
             @click="magicImport"
             :loading="courseSectionImporter.state.loading"
             :disable="unsavedChanges"/>
    </div>

    <ErrorBox v-if="courseSectionsSubmitter.state.error">
      <p>{{ courseSectionsSubmitter.state.error }}</p>
      <ul>
        <li v-for="error in courseSectionsSubmitter.state.errors" :key="error">{{ error }}</li>
      </ul>
    </ErrorBox>

    <SuccessBox v-else-if="courseSectionsSubmitter.state.loaded">
      <p>Your changes have been saved.</p>
    </SuccessBox>

    <ErrorBox v-if="courseSectionImporter.state.error">
      <p>{{ courseSectionImporter.state.error }}</p>
    </ErrorBox>

    <SuccessBox v-else-if="courseSectionImporter.state.loaded">
      <p>Sections have been imported from UB's course database.</p>
    </SuccessBox>

    <ApiFetchContentContainer :api-data-loader="courseSectionsLoader" loading-text="Loading course sections">
      <h5>Lectures</h5>
      <CourseSectionsTable v-model="lectureSections" is-lecture @new-section="newSection"/>

      <h5>Sections</h5>
      <CourseSectionsTable v-model="sectionSections" @new-section="newSection"/>

      <DebugBox>
        <pre>{{ updatedSections }}</pre>
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
import ErrorBox from 'components/Boxes/ErrorBox.vue'
import SuccessBox from 'components/Boxes/SuccessBox.vue'

const courseName = useRoute().params.courseName
const courseSectionsLoader = new PortalApiDataLoader<CourseSectionsResponse>(`/portal/api/course_sections/${courseName}/`)
courseSectionsLoader.fetch()

const courseSectionsSubmitter = new PortalApiDataLoader(`/portal/api/course_sections/${courseName}/`, 'POST')
const courseSectionImporter = new PortalApiDataLoader(`/portal/api/course_sections/${courseName}/import/`, 'POST')

const lectureSections = computed(() => courseSectionsLoader.state.data?.sections.filter(section => section.is_lecture))
const sectionSections = computed(() => courseSectionsLoader.state.data?.sections.filter(section => !section.is_lecture))

const updatedSections = computed(() => courseSectionsLoader.state.data?.sections.filter(section => section.updated))
const unsavedChanges = computed(() => updatedSections.value && updatedSections.value.length > 0)

function updateSections() {
  courseSectionsSubmitter.fetch({
    sections: updatedSections.value,
  })
      .then(() => {
        if (courseSectionsSubmitter.state.error) {
          return
        }
        courseSectionsLoader.fetch()
      })
}

function magicImport() {
  courseSectionImporter.fetch()
      .then(() => {
        if (courseSectionImporter.state.error) {
          return
        }
        courseSectionsLoader.fetch()
      })
}

function newSection(name: string, isLecture: boolean) {
  courseSectionsLoader.state.data?.sections.push({
    name: name,
    is_lecture: isLecture,
    start_time: '00:00:00',
    end_time: '00:00:00',
    days_code: 0,
    updated: true,
  })
}

</script>
