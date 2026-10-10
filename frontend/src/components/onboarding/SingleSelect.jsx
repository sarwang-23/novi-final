"use client";

/* List of options as tappable buttons; picking one submits immediately.
 * Used for input_type "single_select". Options always come from the API
 * response — this component never hardcodes any option set. */
export default function SingleSelect({ options = [], disabled = false, onSubmit }) {
  return (
    <div className="ob-chips" role="group" aria-label="Choose one">
      {options.map((opt) => (
        <button
          key={opt.value}
          type="button"
          className="ob-chip"
          disabled={disabled}
          onClick={() => onSubmit && onSubmit(opt.value, opt.label)}
        >
          <span className="ob-chip-box" />
          <span>{opt.label}</span>
        </button>
      ))}
    </div>
  );
}