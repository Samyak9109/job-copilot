export const JOB_STATUSES = ['applied', 'interview', 'offer', 'rejected']

export const STATUS_META = {
  applied: { label: 'Applied', tone: 'blue' },
  interview: { label: 'Interview', tone: 'amber' },
  offer: { label: 'Offer', tone: 'green' },
  rejected: { label: 'Rejected', tone: 'red' },
}

export const OUTPUT_LABEL = {
  cover_letter: 'Cover letter',
  interview_answer: 'Interview answer',
  resume_summary: 'Resume summary',
  recruiter_message: 'Recruiter message',
  skill_gap_analysis: 'Skill gap',
  interview_prep: 'Interview prep',
}

export const MEMORY_TYPES = [
  ['resume', 'Resume'],
  ['project', 'Project'],
  ['job_description', 'Job description'],
  ['interview_answer', 'Interview answer'],
  ['recruiter_note', 'Recruiter note'],
  ['feedback', 'Feedback'],
  ['other', 'Other'],
]
