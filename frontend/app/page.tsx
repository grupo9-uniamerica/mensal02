"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function Page() {
  const router = useRouter();

  useEffect(() => {
    if (window.location.pathname === "/") {
      router.push("/home"); // Redireciona para /home se estiver na raiz
    }
  }, []);
}