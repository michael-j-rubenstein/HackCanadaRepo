import { useCallback, useEffect, useRef, useState } from "react";
import { io, Socket } from "socket.io-client";
import { Audio } from "expo-av";
import * as FileSystem from "expo-file-system/legacy";

const BACKEND_URL = "http://localhost:8080";

type RecipeState = "idle" | "loading" | "cooking" | "complete" | "error";

interface RecipeMeta {
  title: string;
  total_steps: number;
  summary: string;
}

interface StepInfo {
  step_number: number;
  total_steps: number;
  title: string;
}

export function useRecipeSocket() {
  const socketRef = useRef<Socket | null>(null);
  const soundQueueRef = useRef<string[]>([]);
  const currentSoundRef = useRef<Audio.Sound | null>(null);
  const isPlayingRef = useRef(false);

  const [state, setState] = useState<RecipeState>("idle");
  const [recipeMeta, setRecipeMeta] = useState<RecipeMeta | null>(null);
  const [currentStep, setCurrentStep] = useState<StepInfo | null>(null);
  const [streamedText, setStreamedText] = useState("");
  const [statusMessage, setStatusMessage] = useState("");
  const [error, setError] = useState("");
  const [isPlaying, setIsPlaying] = useState(false);

  const stopAudio = useCallback(async () => {
    soundQueueRef.current = [];
    isPlayingRef.current = false;
    if (currentSoundRef.current) {
      try {
        await currentSoundRef.current.stopAsync();
        await currentSoundRef.current.unloadAsync();
      } catch {}
      currentSoundRef.current = null;
    }
    setIsPlaying(false);
  }, []);

  const playNextInQueue = useCallback(async () => {
    if (isPlayingRef.current) return;
    if (soundQueueRef.current.length === 0) {
      setIsPlaying(false);
      return;
    }

    isPlayingRef.current = true;
    setIsPlaying(true);

    while (soundQueueRef.current.length > 0) {
      const audioBase64 = soundQueueRef.current.shift()!;
      if (!audioBase64) continue;

      try {
        const fileUri = FileSystem.cacheDirectory + `recipe_audio_${Date.now()}.mp3`;
        await FileSystem.writeAsStringAsync(fileUri, audioBase64, {
          encoding: FileSystem.EncodingType.Base64,
        });
        const { sound } = await Audio.Sound.createAsync({ uri: fileUri });
        currentSoundRef.current = sound;

        await new Promise<void>((resolve) => {
          sound.setOnPlaybackStatusUpdate((status) => {
            if (status.isLoaded && status.didJustFinish) {
              resolve();
            }
          });
          sound.playAsync();
        });

        await sound.unloadAsync();
        currentSoundRef.current = null;
      } catch {}
    }

    isPlayingRef.current = false;
    setIsPlaying(false);
  }, []);

  const enqueueAudio = useCallback(
    (audioBase64: string) => {
      if (!audioBase64) return;
      soundQueueRef.current.push(audioBase64);
      if (!isPlayingRef.current) {
        playNextInQueue();
      }
    },
    [playNextInQueue]
  );

  useEffect(() => {
    const socket = io(BACKEND_URL, {
      transports: ["websocket"],
    });
    socketRef.current = socket;

    socket.on("status", (data: { message: string }) => {
      setStatusMessage(data.message);
    });

    socket.on(
      "recipe_found",
      (data: { title: string; total_steps: number; summary: string }) => {
        setRecipeMeta(data);
        setState("loading");
      }
    );

    socket.on(
      "step_start",
      (data: { step_number: number; total_steps: number; title: string }) => {
        setCurrentStep(data);
        setStreamedText("");
        setState("cooking");
      }
    );

    socket.on("step_text", (data: { text: string }) => {
      setStreamedText((prev) => prev + data.text);
    });

    socket.on(
      "step_audio",
      (data: { audio_base64: string; sentence_index: number }) => {
        enqueueAudio(data.audio_base64);
      }
    );

    socket.on("step_end", () => {});

    socket.on(
      "nudge",
      (data: { message: string; audio_base64: string }) => {
        enqueueAudio(data.audio_base64);
      }
    );

    socket.on(
      "recipe_complete",
      (data: { message: string; audio_base64: string }) => {
        setState("complete");
        enqueueAudio(data.audio_base64);
      }
    );

    socket.on("error", (data: { message: string }) => {
      setError(data.message);
      setState("error");
    });

    return () => {
      socket.disconnect();
    };
  }, [enqueueAudio]);

  const reset = useCallback(() => {
    setState("idle");
    setError("");
    setStreamedText("");
    setRecipeMeta(null);
    setCurrentStep(null);
    setStatusMessage("");
  }, []);

  const startRecipe = useCallback(
    (ingredients: string[]) => {
      setState("loading");
      setError("");
      setStreamedText("");
      setRecipeMeta(null);
      setCurrentStep(null);
      setStatusMessage("Starting recipe search...");
      socketRef.current?.emit("start_recipe", { ingredients });
    },
    []
  );

  const completeStep = useCallback(async () => {
    await stopAudio();
    socketRef.current?.emit("step_complete", {});
  }, [stopAudio]);

  const repeat = useCallback(async () => {
    await stopAudio();
    socketRef.current?.emit("repeat", {});
  }, [stopAudio]);

  const skip = useCallback(async () => {
    await stopAudio();
    socketRef.current?.emit("skip", {});
  }, [stopAudio]);

  const goBack = useCallback(async () => {
    await stopAudio();
    socketRef.current?.emit("go_back", {});
  }, [stopAudio]);

  return {
    state,
    recipeMeta,
    currentStep,
    streamedText,
    statusMessage,
    error,
    isPlaying,
    startRecipe,
    completeStep,
    repeat,
    skip,
    goBack,
    stopAudio,
    reset,
  };
}
