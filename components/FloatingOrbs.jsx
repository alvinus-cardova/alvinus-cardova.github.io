"use client";

import { gsap } from "gsap";
import { useEffect, useRef } from "react";

const orbs = [
  { top: "8%", left: "6%", size: 180, blur: 10, color: "rgba(11, 117, 215, 0.32)" },
  { top: "18%", right: "4%", size: 220, blur: 14, color: "rgba(15, 138, 138, 0.28)" },
  { bottom: "10%", left: "8%", size: 250, blur: 18, color: "rgba(34, 120, 222, 0.22)" },
  { bottom: "4%", right: "10%", size: 160, blur: 8, color: "rgba(19, 142, 167, 0.25)" }
];

export default function FloatingOrbs() {
  const refs = useRef([]);

  useEffect(() => {
    const ctx = gsap.context(() => {
      refs.current.forEach((el, index) => {
        if (!el) return;
        gsap.to(el, {
          x: index % 2 === 0 ? 24 : -24,
          y: index % 2 === 0 ? -30 : 30,
          duration: 5.5 + index,
          repeat: -1,
          yoyo: true,
          ease: "sine.inOut"
        });
      });
    });

    return () => ctx.revert();
  }, []);

  return (
    <div aria-hidden className="pointer-events-none fixed inset-0 -z-10 overflow-hidden">
      {orbs.map((orb, index) => (
        <span
          key={`${orb.color}-${index}`}
          ref={(el) => {
            refs.current[index] = el;
          }}
          className="absolute rounded-full"
          style={{
            ...orb,
            width: `${orb.size}px`,
            height: `${orb.size}px`,
            backgroundColor: orb.color,
            filter: `blur(${orb.blur}px)`
          }}
        />
      ))}
    </div>
  );
}
