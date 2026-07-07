interface PdfIconProps {
  className?: string;
}

export function PdfIcon({ className = "h-16 w-16" }: PdfIconProps) {
  return (
    <svg
      className={className}
      viewBox="0 0 64 64"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
    >
      <rect x="8" y="4" width="40" height="56" rx="4" fill="#FEE2E2" stroke="#EF4444" strokeWidth="2" />
      <path
        d="M20 18h24M20 28h24M20 38h16"
        stroke="#EF4444"
        strokeWidth="2"
        strokeLinecap="round"
      />
      <rect x="34" y="34" width="22" height="22" rx="4" fill="#EF4444" />
      <text
        x="45"
        y="49"
        textAnchor="middle"
        fill="white"
        fontSize="10"
        fontWeight="700"
        fontFamily="Arial, sans-serif"
      >
        PDF
      </text>
    </svg>
  );
}
