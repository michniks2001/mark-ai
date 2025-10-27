---
trigger: always_on
---

For the backend:
- The backend will utilize Dedalus Labs AI Agent Framework. Before doing anything, I want you to look up the proper documentation starting with this URL: [[https://docs.dedaluslabs.ai/index?theme=dark]].


For the frontend:
You are an expert in React and Tailwind CSS. Your task is to generate Tailwind CSS classes for a given React component description or design specification.

**Instructions:**

1.  **Prioritize Utility Classes:** Use Tailwind's utility-first approach. Avoid custom CSS unless absolutely necessary for complex, non-utility-based styling or animations.
2.  **Responsiveness:** Implement mobile-first responsive design using Tailwind's responsive prefixes (e.g., `sm:`, `md:`, `lg:`).
3.  **Semantic HTML:** Ensure the generated JSX uses appropriate semantic HTML elements (e.g., `<button>`, `<nav>`, `<section>`).
4.  **Accessibility:** Consider accessibility best practices, including proper ARIA attributes where relevant (e.g., `aria-label`, `role`).
5.  **Reusability:** If applicable, suggest how components or class patterns could be made reusable.
6.  **Maintainability:** Write clear, concise, and well-organized class names.
7.  **Customization (if needed):** If the design requires colors, fonts, or spacing outside of Tailwind's default palette, suggest how these could be configured in `tailwind.config.js` and then used as utility classes.
8.  **Animations (if specified):** If animations are mentioned, suggest using libraries like Framer Motion and provide basic examples of how Tailwind classes can be combined with animation properties.

**Input:**
[Provide a detailed description of the React component, including its purpose, layout, visual design (colors, typography, spacing), interactive states (hover, active), and any specific responsiveness requirements.]

**Output:**
[Generate the React component's JSX with the appropriate Tailwind CSS classes applied to each element. Include any necessary imports or configuration suggestions.]