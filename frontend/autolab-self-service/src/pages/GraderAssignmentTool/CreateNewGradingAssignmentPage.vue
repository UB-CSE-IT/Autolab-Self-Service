<template>
  <q-page class="q-px-lg q-mx-auto" style="max-width: 1000px;">

    <div class="button-row q-my-lg">
      <q-btn icon="west" label="Back to Autolab Assessments" color="primary" :to="{name: 'grader-assignment-tool-autolab-assessments'}"/>
    </div>
      TODO!


  </q-page>
</template>

<script setup lang="ts">
import {useRoute} from 'vue-router'
import {PortalApiDataLoader} from 'src/utilities/PortalApiDataLoader'
import ApiFetchContentContainer from 'components/ApiFetchContentContainer.vue'

const courseName = useRoute().params.courseName
const assessmentName = useRoute().params.assessmentName



</script>
