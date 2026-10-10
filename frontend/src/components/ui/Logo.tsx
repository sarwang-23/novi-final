import Image from "next/image";
import Link from "next/link";

export default function Logo({ className = "" }: { className?: string }) {
  return (
    <Link
      href="/"
      className={`group inline-flex items-center gap-2.5 ${className}`}
      aria-label="Novi — home"
    >
      <span className="relative grid size-9 place-items-center overflow-hidden rounded-xl shadow-glow transition-transform duration-300 group-hover:scale-105">
        <Image
          src="/icon.png"
          alt="Novi logo"
          fill
          sizes="36px"
          className="object-contain"
        />
      </span>
      <span className="font-display text-xl font-bold tracking-tight">
        Novi
      </span>
    </Link>
  );
}