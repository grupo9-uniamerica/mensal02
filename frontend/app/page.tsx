"use client";

import dynamic from "next/dynamic";

const home = dynamic(() => import("./home/page"), { ssr: false });

export default function Page() {
  return (
    <div>
      {<Home/>}
    </div>
  );
}
