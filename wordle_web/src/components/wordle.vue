<template>
	<div class="min-h-screen flex flex-col items-center justify-center space-y-6 bg-gray-50 p-4">
		<h1 class="text-2xl font-bold text-gray-800">Submit Form</h1>

		<div v-if="submittedOtps.length" style="margin-top: 1em;">
			<p>Submitted OTPs:</p>
			<ul>
				<li v-for="(otp, index) in submittedOtps" :key="index" style="margin-bottom: 4px;">
					<n-input-otp :value="otp" :length="5" disabled />
				</li>
			</ul>
		</div>

		<n-input-otp v-model:value="currentOtp" :length="5" :disabled="inputDisabled" :allow-input="onlyAllowEnglish" />

		<div class="mt-20 flex flex-row justify-center" v-if="show_submit_button">
			<el-button size="large" color="#34498E" :width="70"
				class="text-white hover:text-white focus:text-white active:text-white text-2xl" @click="submit">
				Submit
			</el-button>
		</div>
	</div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { NInputOtp } from 'naive-ui'
import axios from 'axios'
import { useRouter } from 'vue-router'

const router = useRouter()


const onlyAllowEnglish = (value: string) => !value || /^[a-zA-Z]+$/.test(value)

const currentOtp = ref<string[]>([])
const submittedOtps = ref<string[][]>([])
const inputDisabled = ref(false)
const show_submit_button = ref(false)

watch(currentOtp, () => {
	if (currentOtp.value.join('').length === 5) {
		show_submit_button.value = true
	}
})

async function submit() {
	submittedOtps.value.push([...currentOtp.value])
	const submitdata = new FormData()
	submitdata.append('word', currentOtp.value.join('').toLowerCase())
	currentOtp.value = []
	show_submit_button.value = false

	const response = await axios.post(`/user_submit_word/`, submitdata, {
		baseURL: '/api',
		timeout: 10000,
	})
	const { data } = response
	console.log(data)
	console.log(typeof data.result)
	if (data.result === 'true') {
		windowSuccessMessage(data.message)
	} else {
		windowErrorMessage(data.message)
	}
}
</script>
