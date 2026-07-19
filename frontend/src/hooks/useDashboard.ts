"use client";

import {
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react";

import {
  getReplayFrame,
  getReplayMetadata,
} from "@/lib/api";

import {
  ReplayMetadata,
  Station,
  SummaryResponse,
} from "@/types/airmind";

const PLAYBACK_INTERVAL_MS = 1600;

export function useDashboard() {
  const [summary, setSummary] =
    useState<SummaryResponse | null>(null);

  const [stations, setStations] =
    useState<Station[]>([]);

  const [metadata, setMetadata] =
    useState<ReplayMetadata | null>(null);

  const [currentFrame, setCurrentFrame] =
    useState(0);

  const [timestamp, setTimestamp] =
    useState<string | null>(null);

  const [loading, setLoading] =
    useState(true);

  const [frameLoading, setFrameLoading] =
    useState(false);

  const [error, setError] =
    useState<string | null>(null);

  const [isPlaying, setIsPlaying] =
    useState(false);

  const requestIdRef = useRef(0);

  const loadFrame = useCallback(
    async (
      frameIndex: number,
      showLoader = true,
    ) => {
      const requestId = ++requestIdRef.current;

      try {
        if (showLoader) {
          setFrameLoading(true);
        }

        setError(null);

        const frameData =
          await getReplayFrame(frameIndex);

        if (
          requestId !== requestIdRef.current
        ) {
          return;
        }

        setSummary(frameData.summary);
        setStations(frameData.stations);
        setTimestamp(frameData.timestamp_utc);
      } catch (err) {
        if (
          requestId !== requestIdRef.current
        ) {
          return;
        }

        setIsPlaying(false);

        setError(
          err instanceof Error
            ? err.message
            : "Unable to load replay frame.",
        );
      } finally {
        if (
          requestId === requestIdRef.current
        ) {
          setFrameLoading(false);
        }
      }
    },
    [],
  );

  useEffect(() => {
    async function initialiseReplay() {
      try {
        setLoading(true);
        setError(null);

        const replayMetadata =
          await getReplayMetadata();

        setMetadata(replayMetadata);
        setCurrentFrame(
          replayMetadata.first_frame,
        );

        await loadFrame(
          replayMetadata.first_frame,
          false,
        );
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Unable to initialise replay.",
        );
      } finally {
        setLoading(false);
      }
    }

    initialiseReplay();
  }, [loadFrame]);

  useEffect(() => {
    if (!metadata) {
      return;
    }

    loadFrame(currentFrame);
  }, [
    currentFrame,
    metadata,
    loadFrame,
  ]);

  useEffect(() => {
    if (!isPlaying || !metadata) {
      return;
    }

    const interval = window.setInterval(
      () => {
        setCurrentFrame((previousFrame) => {
          if (
            previousFrame >=
            metadata.last_frame
          ) {
            setIsPlaying(false);
            return metadata.last_frame;
          }

          return previousFrame + 1;
        });
      },
      PLAYBACK_INTERVAL_MS,
    );

    return () => {
      window.clearInterval(interval);
    };
  }, [isPlaying, metadata]);

  function play() {
    if (!metadata) {
      return;
    }

    if (
      currentFrame >= metadata.last_frame
    ) {
      setCurrentFrame(
        metadata.first_frame,
      );
    }

    setIsPlaying(true);
  }

  function pause() {
    setIsPlaying(false);
  }

  function togglePlayback() {
    if (isPlaying) {
      pause();
    } else {
      play();
    }
  }

  function goToPreviousFrame() {
    if (!metadata) {
      return;
    }

    setIsPlaying(false);

    setCurrentFrame((previousFrame) =>
      Math.max(
        metadata.first_frame,
        previousFrame - 1,
      ),
    );
  }

  function goToNextFrame() {
    if (!metadata) {
      return;
    }

    setIsPlaying(false);

    setCurrentFrame((previousFrame) =>
      Math.min(
        metadata.last_frame,
        previousFrame + 1,
      ),
    );
  }

  function goToFrame(
    frameIndex: number,
  ) {
    if (!metadata) {
      return;
    }

    setIsPlaying(false);

    const safeFrame = Math.min(
      metadata.last_frame,
      Math.max(
        metadata.first_frame,
        frameIndex,
      ),
    );

    setCurrentFrame(safeFrame);
  }

  return {
    summary,
    stations,
    metadata,
    currentFrame,
    timestamp,
    loading,
    frameLoading,
    error,
    isPlaying,
    togglePlayback,
    goToPreviousFrame,
    goToNextFrame,
    goToFrame,
  };
}