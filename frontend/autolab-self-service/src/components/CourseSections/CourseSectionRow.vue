<template>
  <tr :class="{'bg-yellow-2': localSection?.updated}">
    <td>{{ props.modelValue.name }}</td>
    <td>
      <q-input dense v-model="startTime" style="min-width: 120px;">
        <template v-slot:append>
          <q-icon name="access_time" class="cursor-pointer">
            <q-popup-proxy cover transition-show="scale" transition-hide="scale">
              <q-time v-model="startTime" mask="HH:mm:ss">
                <div class="row items-center justify-end">
                  <q-btn v-close-popup label="Close" color="primary" flat/>
                </div>
              </q-time>
            </q-popup-proxy>
          </q-icon>
        </template>
      </q-input>
    </td>
    <td>
      <q-input dense v-model="endTime" style="min-width: 120px;">
        <template v-slot:append>
          <q-icon name="access_time" class="cursor-pointer">
            <q-popup-proxy cover transition-show="scale" transition-hide="scale">
              <q-time v-model="endTime" mask="HH:mm:ss">
                <div class="row items-center justify-end">
                  <q-btn v-close-popup label="Close" color="primary" flat/>
                </div>
              </q-time>
            </q-popup-proxy>
          </q-icon>
        </template>
      </q-input>
    </td>
    <td>
      <q-select dense
                multiple
                :options="dayOptions"
                :display-value="selectedDaysDisplayValue"
                v-model="selectedDays"
                style="width: 200px;"
      />
    </td>
    <td>
      <span v-if="localSection.updated" class="text-red">Not saved</span>
    </td>
  </tr>
</template>

<script setup lang="ts">

import {CourseSection} from 'src/types/CourseSectionsTypes'
import {computed, PropType, ref} from 'vue'

const props = defineProps({
  modelValue: {
    type: Object as PropType<CourseSection>,
    required: true,
  },
})

const emits = defineEmits(['update:modelValue'])

const localSection = ref<CourseSection>(props.modelValue)

const dayOptions = [
  'Sunday',
  'Monday',
  'Tuesday',
  'Wednesday',
  'Thursday',
  'Friday',
  'Saturday',
]

const dayAbbreviations: { [key: string]: string } = {
  'Sunday': 'U',
  'Monday': 'M',
  'Tuesday': 'T',
  'Wednesday': 'W',
  'Thursday': 'R',
  'Friday': 'F',
  'Saturday': 'S',
}

const startTime = computed({
  get: () => props.modelValue?.start_time,
  set: (value: string) => {
    localSection.value.start_time = value
    localSection.value.updated = true
    emits('update:modelValue', localSection.value)
  },
})

const endTime = computed({
  get: () => props.modelValue?.end_time,
  set: (value: string) => {
    localSection.value.end_time = value
    localSection.value.updated = true
    emits('update:modelValue', localSection.value)
  },
})

const selectedDays = computed({
  get: () => daysCodeToDayNames(props.modelValue?.days_code),
  set: (value: string[]) => {
    localSection.value.days_code = dayNamesToDaysCode(value)
    localSection.value.updated = true
    emits('update:modelValue', localSection.value)
  },
})

const selectedDaysDisplayValue = computed(() => {
  const length = selectedDays.value.length
  if (length === 0) {
    return 'None'
  }
  if (length === 7) {
    return 'Every day'
  }
  if (length == 1) {
    return selectedDays.value[0]
  } else {
    return selectedDays.value.map(day => dayAbbreviations[day]).join('')
  }
})

function daysCodeToDayNames(daysCode: number): string[] {
  const days = []
  for (let i = 0; i < 7; i++) {
    if (daysCode & (1 << i)) {
      days.push(dayOptions[i])
    }
  }
  return days
}

function dayNamesToDaysCode(dayNames: string[]): number {
  let daysCode = 0
  for (const dayName of dayNames) {
    daysCode |= 1 << dayOptions.indexOf(dayName)
  }
  return daysCode
}

</script>

<style scoped lang="scss">

</style>
