<template>
  <InfoBox v-if="props.modelValue?.length === 0">
    <p>No {{ sectionTypeName.toLowerCase() }}s have been created yet.</p>
  </InfoBox>

  <q-markup-table v-else>
    <thead>
    <tr style="text-align: left">
      <th>{{ sectionTypeName }} Name</th>
      <th>Start Time</th>
      <th>End Time</th>
      <th>Days</th>
      <th></th>
    </tr>
    </thead>
    <tbody>
    <CourseSectionRow v-for="section in props.modelValue"
                      :key="section.name"
                      :model-value="section"/>
    </tbody>
  </q-markup-table>

  <form @submit.prevent="addSection">
    <div class="button-row">
      <q-input dense
               v-model="newSectionName"
               :label="`New ${sectionTypeName} Name`"
               class="q-mt-md"
      />
      <q-btn icon="add"
             :label="`Add ${sectionTypeName}`"
             color="primary"
             class="q-mt-md"
             type="submit"
             :disable="addDisabled"/>
    </div>
    <p v-if="addDisabled && addDisabledMessage" class="q-mt-sm text-red">
      <q-icon name="warning" class="q-mr-sm"/>
      {{ addDisabledMessage }}
    </p>
  </form>
</template>

<script setup lang="ts">

import {computed, PropType, ref} from 'vue'
import {CourseSection} from 'src/types/CourseSectionsTypes'
import CourseSectionRow from 'components/CourseSections/CourseSectionRow.vue'
import InfoBox from 'components/Boxes/InfoBox.vue'

const props = defineProps({
  modelValue: {
    type: Array as PropType<CourseSection[]>,
    required: true,
  },
  isLecture: {
    type: Boolean,
  },
})

const emits = defineEmits(['newSection'])

const sectionTypeName = computed(() => props.isLecture ? 'Lecture' : 'Section')
const newSectionName = ref('')

const addDisabled = computed(() => {
  return newSectionName.value === ''
    || newSectionNameAlreadyExists()
    || newSectionNameHasLeadingOrTrailingWhitespace()
})

const addDisabledMessage = computed(() => {
  if (newSectionNameAlreadyExists()) {
    return 'That section already exists'
  } else if (newSectionNameHasLeadingOrTrailingWhitespace()) {
    return 'That section name contains a leading or trailing whitespace'
  }

  return ''
})

function addSection() {
  emits('newSection', newSectionName.value, props.isLecture)
  newSectionName.value = ''
}

function newSectionNameAlreadyExists() {
  return props.modelValue.some(section => section.name === newSectionName.value)
}

function newSectionNameHasLeadingOrTrailingWhitespace() {
  return newSectionName.value[0] === ' '
    || newSectionName.value[newSectionName.value.length - 1] === ' '
}


</script>

<style scoped lang="scss">

</style>
