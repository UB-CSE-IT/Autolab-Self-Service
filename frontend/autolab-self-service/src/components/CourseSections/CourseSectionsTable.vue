<template>
  <InfoBox v-if="props.modelValue?.length === 0">
    <p>No {{ props.typeName }}s have been created yet.</p>
  </InfoBox>

  <q-markup-table v-else>
    <thead>
    <tr style="text-align: left">
      <th>Section Name</th>
      <th>Start Time</th>
      <th>End Time</th>
      <th>Days</th>
    </tr>
    </thead>
    <tbody>
    <CourseSectionRow v-for="section in props.modelValue"
                      :key="section.name"
                      :model-value="section"/>
    </tbody>
  </q-markup-table>
</template>

<script setup lang="ts">

import {PropType} from 'vue'
import {CourseSection} from 'src/types/CourseSectionsTypes'
import CourseSectionRow from 'components/CourseSections/CourseSectionRow.vue'
import InfoBox from 'components/Boxes/InfoBox.vue'

const props = defineProps({
  modelValue: {
    type: Array as PropType<CourseSection[]>,
    required: true,
  },
  typeName: {
    type: String,
    required: true,
  },
})

</script>

<style scoped lang="scss">

</style>
