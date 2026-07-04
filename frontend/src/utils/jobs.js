export function selectedJobPatch(jobs, id, currentDescription) {
  const job = jobs.find((j) => String(j.id) === id)
  return {
    job_id: id,
    job_description: job?.jd_text || currentDescription,
  }
}
