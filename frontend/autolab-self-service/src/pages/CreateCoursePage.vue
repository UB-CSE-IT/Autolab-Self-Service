<template>
  <q-page class="q-px-lg q-mx-auto" style="max-width: 1000px;">
    <h3>Create an Autolab Course</h3>
    <div>

      <div v-if="state.stage === 0">
        <q-btn icon="west" label="Back to portal home" color="primary" to="/"/>
        <h4>Step 1: Choose a Course</h4>
        <p>Here are the current and upcoming courses you're scheduled to teach. You'll be able to confirm all the
          details before the course is actually created. If you don't see the course you'd
          like, <a target="_blank" href="https://autolab.cse.buffalo.edu/contact">contact us</a> to create a
          custom one.</p>
        <div v-if="userStore.userData.isAdmin" class="admin-info">
          <p>As an admin, you can create courses for any instructor.</p>
          <q-form @submit="loadCourses">
            <q-input v-model="state.username" label="Instructor username">
              <q-btn icon="east" color="primary" type="submit"/>
            </q-input>
          </q-form>
        </div>
        <div v-if="state.loadingCourses">
          Loading...
        </div>
        <div v-else-if="state.errorLoadingCourses">
          Error loading courses: {{ state.errorMessage }}
        </div>
        <div v-else class="flex">
          <div v-for="course in state.data.data.courses" :key="course.uniqueIdentifier">
            <div class="autolab-card">
              <div class="header">
                {{ course.suggestedName }} ({{ course.semesterCode }})
              </div>
              <div class="element">
                {{ course.courseType }} by {{ course.instructor }}@buffalo.edu
              </div>
              <div class="element">
                {{ course.term }}
              </div>
              <div v-if="course.crosslistedIdentifier" class="element">
                Using first alphabetical cross-listed course name
              </div>
              <div v-else class="element">
                Not cross-listed
              </div>
              <div class="element">
                URL will be .../courses/{{ course.technicalName }}
              </div>
              <div class="actions">
                <q-btn label="Create this course" color="white" text-color="primary" flat
                       @click="moveToStage1(course)"/>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-else-if="state.stage === 1">
        <q-btn icon="west" label="Back to my courses" color="primary" @click="moveToStage0"/>
        <h4>Step 2: Customization</h4>
        <h6 class="q-my-none">Choose the display name for the course</h6>
        <ul>
          <li>This will be displayed in the list of courses and at the top of the course page.</li>
          <li>This can always be changed later in Autolab.</li>
          <li>For consistency:
            <ul>
              <li><i>UPPERCASE</i> the subject(s)</li>
              <li>Insert a <i>space</i> between the subject and the number</li>
              <li>If the course is cross-listed:
                <ul>
                  <li>Include all substantial cross-listed offerings. Small courses like CSE 503 may be omitted.</li>
                  <li>If there are multiple subjects, put the CSE entry first, then put the other subjects in
                    alphabetical order
                  </li>
                  <li>Within a subject, list the course numbers in ascending order</li>
                  <li>Separate the courses with a <i>slash</i> (without spaces on either side)</li>
                </ul>
              </li>
              <li>Follow the last course number with a <i>colon and space</i></li>
              <li>Finally, "nickname" the course in <i>Title Case</i>.</li>
            </ul>
          </li>
          <li>Here are some examples we like to use. Note the spacing, capitalization, and punctuation.
            <ul>
              <li>CSE 116: Computer Science 2</li>
              <li>CSE 220: Systems Programming</li>
              <li>CSE 468/CSE 568: Robotics Algorithms
                <q-icon color="primary" name="shuffle">
                  <q-tooltip anchor="top middle" self="center middle">Cross-listed</q-tooltip>
                </q-icon>
              </li>
              <li>CSE 486/586: Distributed Systems
                <q-icon color="primary" name="shuffle">
                  <q-tooltip anchor="top middle" self="center middle">Cross-listed</q-tooltip>
                </q-icon>
              </li>
              <li>CSE 491/CSE 596: Theory of Computation
                <q-icon color="primary" name="shuffle">
                  <q-tooltip anchor="top middle" self="center middle">Cross-listed</q-tooltip>
                </q-icon>
              </li>
              <li>CSE 575/APY 526/LIN 575/PHI 575/PSY 575: Intro to Cognitive Science
                <q-icon color="primary" name="shuffle">
                  <q-tooltip anchor="top middle" self="center middle">Cross-listed</q-tooltip>
                </q-icon>
                <q-icon color="primary" name="sentiment_very_dissatisfied">
                  <q-tooltip anchor="top middle" self="center middle">I can't believe this one is real</q-tooltip>
                </q-icon>
              </li>
            </ul>
          </li>
          <li>We've chosen a good default ({{ state.stage0.selectedCourse.suggestedName }}), but you're welcome to
            change it.
          </li>
        </ul>
        <q-input outlined v-model="state.stage1.typedDisplayName" input-style="font-size: 20px;"/>
        <h6 class="q-mb-none">Preview</h6>
        <div class="row justify-center">
          <div class="autolab-card">
            <div class="header">
              {{ state.stage1.typedDisplayName }} ({{ state.stage0.selectedCourse.semesterCode }})
            </div>
            <div class="element">
              Genetic Algorithm
            </div>
            <div class="element">
              Malloc
            </div>
            <div class="element">
              Bug2
            </div>
            <div class="actions">
              <q-btn label="Course page" color="white" text-color="primary" flat/>
              <q-btn label="Gradebook" color="white" text-color="primary" flat/>
            </div>
          </div>
        </div>
        <div class="full-width row reverse q-ma-xl">
          <div>
            <q-btn icon-right="east" label="Continue" color="primary" @click="moveToStage2"/>
          </div>
        </div>
      </div>

      <div v-else-if="state.stage === 2">
        <q-btn icon="west" label="Back to customization" color="primary"
               @click="moveToStage1(state.stage0.selectedCourse)"/>
        <h4>Step 3: Confirmation</h4>
        <h6 class="q-mb-none">You're about to create this course on Autolab</h6>
        <p>If it looks good to you, click "confirm." If you'd like to change something beyond what this portal allows,
          feel free to <a target="_blank" href="https://autolab.cse.buffalo.edu/contact">contact CSE IT</a> for a custom
          solution.</p>
        <div class="row justify-center">
          <div class="autolab-card">
            <div class="header">
              {{ state.stage2.displayName }} ({{ state.stage0.selectedCourse.semesterCode }})
            </div>
            <div class="element">
              First instructor: {{ state.stage0.selectedCourse.instructor }}@buffalo.edu
            </div>
            <div class="element">
              Season: {{ state.stage0.selectedCourse.term }}
            </div>
            <div class="element">
              URL: https://autolab.cse.buffalo.edu/courses/{{ state.stage0.selectedCourse.technicalName }}
            </div>
            <div class="element">
              Start and end dates will be set automatically
            </div>
            <div class="actions">
              <q-btn @click="moveToStage3" label="Confirm" color="white" text-color="primary" flat/>
            </div>
          </div>
        </div>
      </div>

      <div v-else-if="state.stage === 3">
        <div v-if="state.stage3.loading">
          <h4>Waiting for response from Autolab...</h4>
        </div>
        <div v-else-if="state.stage3.error">
          <q-btn icon="west" label="Try again" color="primary" @click="moveToStage2"/>
          <h4>Error</h4>
          <p>{{ state.stage3.errorMessage }}</p>
          <p>If that's not descriptive enough to resolve the problem,
            <a target="_blank" href="https://autolab.cse.buffalo.edu/contact">contact us</a>.</p>
        </div>
        <div v-else>
          <q-btn icon="west" label="Back to portal home" color="primary" to="/"/>
          <h4>Success!</h4>
          <p>{{ state.stage3.response.message }}</p>
          <q-btn :href="state.stage3.response.location" label="Go to course page" color="primary"/>
        </div>
      </div>
    </div>


    <div style="height: 100px;"></div>
  </q-page>
</template>

<script setup lang="ts">
import {reactive, ref} from 'vue';
import {useUserStore} from 'stores/UserStore';
import {MyCoursesResponse} from "src/types/MyCoursesResponse";
import {Course} from "src/types/Course";
import {useRouter} from "vue-router";

const userStore = useUserStore()
const router = useRouter()

// Stage 0 is picking the course, 1 is choosing the name, 2 is the final confirmation, 3 is after confirmation

const state = reactive({
  stage: 0,
  data: [] as MyCoursesResponse[],
  loadingCourses: false,
  errorLoadingCourses: false,
  errorMessage: '',
  username: userStore.userData.username,
  stage0: {
    selectedCourse: null as Course | null,
  },
  stage1: {
    typedDisplayName: '',
  },
  stage2: {
    displayName: '',
  },
  stage3: {
    loading: false,
    error: false,
    errorMessage: '',
    success: false,
    response: null as any,
  },
})

function loadCourses() {
  // fetch(`/portal/api/my-courses/${state.username}/`)
  state.stage = 0
  state.data = [] as MyCoursesResponse[]
  state.loadingCourses = true
  state.errorLoadingCourses = false
  state.errorMessage = ''
  fetch(`/portal/api/my-courses/${state.username}/`)
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        state.data = data;
        state.loadingCourses = false
      } else {
        return Promise.reject(data)
      }
    })
    .catch(error => {
      state.errorLoadingCourses = true
      state.loadingCourses = false
      state.errorMessage = error.error
    })
}

function scrollToTop() {
  window.scrollTo(0, 0)
}

function moveToStage0() {
  scrollToTop()
  state.stage = 0
  state.stage0.selectedCourse = null as Course | null
}

function moveToStage1(course: Course) {
  scrollToTop()
  if (state.stage < 1) {
    // Only update the display name if moving forwards, keep their custom option if they go back
    state.stage1.typedDisplayName = course.suggestedName
  }
  state.stage0.selectedCourse = course;
  state.stage2.displayName = ''
  state.stage = 1
}

function moveToStage2() {
  scrollToTop()
  state.stage2.displayName = state.stage1.typedDisplayName
  state.stage = 2
}

function moveToStage3() {
  scrollToTop()
  requestCreateCourse()
  state.stage = 3
}

function requestCreateCourse() {
  const data = {
    uniqueIdentifier: state.stage0.selectedCourse?.uniqueIdentifier,
    displayName: state.stage2.displayName,
  }

  state.stage3.error = false
  state.stage3.loading = true
  state.stage3.errorMessage = ''
  state.stage3.success = false

  fetch('/portal/api/create-course/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        state.stage3.success = true
        state.stage3.response = data.data
      } else {
        return Promise.reject(data)
      }
    })
    .catch(error => {
      state.stage3.error = true
      state.stage3.errorMessage = error.error
    })
    .finally(
      () => {
        state.stage3.loading = false
      }
    )
}

loadCourses()

</script>
