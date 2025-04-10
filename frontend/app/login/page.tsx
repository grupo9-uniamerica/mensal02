"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function LoginPage() {
  const [username, setusername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const router = useRouter(); // Inicializa o roteamento

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    const formData = new URLSearchParams();
    formData.append("username", username);
    formData.append("password", password);


    try {
      const response = await fetch("/token", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: formData,
      });      

      if (!response.ok) throw new Error("Credenciais inválidas");

      const data = await response.json();
      localStorage.setItem("jwt", data.access_token); // Armazena o token
      alert("Login realizado com sucesso!");
      router.push("/home");
    } catch (err) {
      console.error("Erro ao fazer login:", err);

      // Verifica se err é uma instância de Error
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Erro ao fazer login. Tente novamente.");
      }
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.loginBox}>
        <h2 style={styles.title}>Login</h2>
        {error && <p style={styles.error}>{error}</p>}
        <form onSubmit={handleSubmit} style={styles.form}>
          <input
            type="text"
            placeholder="Digite seu nome de usuário"
            value={username}
            onChange={(e) => setusername(e.target.value)}
            required
            style={styles.input}
          />
          <input
            type="password"
            placeholder="Digite sua senha"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            style={styles.input}
          />
          <button type="submit" style={styles.button}>Entrar</button>
        </form>
      </div>
    </div>
  );
}

const styles = {
  container: {
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    height: "100vh",
    background: "linear-gradient(45deg, #6a11cb, #2575fc)",
    color: "black",
  } as React.CSSProperties, // Define tipagem correta
  loginBox: {
    background: "white",
    padding: "30px",
    borderRadius: "10px",
    boxShadow: "0 4px 10px rgba(0, 0, 0, 0.1)",
    textAlign: "center" as const, // Corrige tipagem
    width: "300px",
    color: "black",
  } as React.CSSProperties,
  title: {
    marginBottom: "20px",
    color: "black",
  } as React.CSSProperties,
  error: {
    color: "red",
    marginBottom: "10px",
  } as React.CSSProperties,
  form: {
    display: "flex",
    flexDirection: "column",
  } as React.CSSProperties,
  input: {
    width: "100%",
    padding: "10px",
    margin: "10px 0",
    border: "1px solid #ccc",
    borderRadius: "5px",
    fontSize: "16px",
    color: "black",
  } as React.CSSProperties,
  button: {
    width: "100%",
    padding: "10px",
    background: "#6a11cb",
    color: "white",
    border: "none",
    borderRadius: "5px",
    cursor: "pointer",
    fontSize: "16px",
    marginTop: "10px",
  } as React.CSSProperties,
};