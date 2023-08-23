<template>
  <div class="course-box">
    <p class="text-h5">{{ course.display_name }} ({{ course.semester }})</p>
    <p class="text-h6 subtext">({{ course.name }}, {{ course.role }})</p>
    <q-btn
        @click="importFromAutolab"
        label="Import from Autolab"
        color="primary"
        class="q-mt-sm"
        icon="download"
        :loading="autolabCourseImporter.state.loading"
    />

    <ErrorBox v-if="autolabCourseImporter.state.error">
      <p>{{ autolabCourseImporter.state.error }}</p>
    </ErrorBox>
    <SuccessBox v-if="autolabCourseImporter.state.data">
      <p>Successfully imported course from Autolab!</p>
      <RouterLink :to="{name: 'grader-assignment-tool-course', params: {courseName: course.name}}">
        <q-btn class="q-mt-sm" label="Go to course" color="primary" icon-right="arrow_forward"/>
      </RouterLink>
    </SuccessBox>
  </div>
</template>


<script setup lang="ts">
import {GatAutolabCourse, GatCourse} from 'src/types/GradingAssignmentToolTypes'
import {PropType} from 'vue'
import {PortalApiDataLoader} from 'src/utilities/PortalApiDataLoader'
import ErrorBox from 'components/Boxes/ErrorBox.vue'
import SuccessBox from 'components/Boxes/SuccessBox.vue'

const props = defineProps({
  course: {
    type: Object as PropType<GatAutolabCourse>,
    required: true,
  },
})

const emits = defineEmits(['courseImported'])

const autolabCourseImporter = new PortalApiDataLoader(`/portal/api/gat/create-course/${props.course?.name}/`, 'POST')

function importFromAutolab() {
  autolabCourseImporter.fetch()
      .then(() => {
        if (autolabCourseImporter.state.error === undefined) {
          const course = {...props.course} as GatCourse
          course.display_name += ` (${props.course?.semester})`
          emits('courseImported', course)
        }
      })
}

</script>

<style scoped lang="scss">


</style>
