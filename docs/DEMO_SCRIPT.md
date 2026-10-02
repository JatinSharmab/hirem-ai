# HireMe AI interview walkthrough

Use the new Next.js frontend locally, or the verified Vercel URL once published. The existing Streamlit site remains a fallback. Allow time for the free API to wake up and use a synthetic resume.

1. **0:00 ? Explain the problem.** AI resume rewriting can invent claims; HireMe AI makes evidence inspectable.
2. **0:30 ? Upload and consent.** Use a text-based PDF/DOCX under 4 MiB. Explain that Python parses and Gemini extracts.
3. **1:10 ? Review facts.** Open a source excerpt and review the facts individually. Review is user approval, not identity verification.
4. **1:50 ? Import a job.** Paste a realistic synthetic JD or use a company Greenhouse/Lever/Ashby identifier. UNKNOWN is not OPEN.
5. **2:20 ? Analyze explicitly.** Show mandatory/preferred skills, experience and missing fields. Explain backend caching.
6. **2:50 ? Match.** Show the Career Fit Score, one evidence ID and one gap. Explain the seven weights and the two proxy factors.
7. **3:30 ? Tailor.** Consent to reviewed-evidence selection. Inspect a bullet, source IDs and PASSED/FAILED status.
8. **4:05 ? Export.** Approve the extract and download PDF/DOCX. Python verifies it again; this is an extract, not a full resume reconstruction.
9. **4:25 ? Track.** Save an application and update its stage. Explain that the user applies on the official site.
10. **4:45 ? Architecture and privacy.** Show the BFF boundary, temporary workspace and clear-data action.

Do not show synthetic fixtures as real provider results. Do not claim live vector search, autonomous agents, production LangGraph traces, global market intelligence or automatic job applications. If the provider is unavailable, show the recovery state and the dated acceptance report.

For spoken explanations and questions, use [FRONTEND_INTERVIEW_GUIDE.md](FRONTEND_INTERVIEW_GUIDE.md).
