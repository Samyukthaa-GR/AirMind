"use client";

import {
  Joyride,
  STATUS,
  type EventData,
  type Step,
  type Styles,
} from "react-joyride";

interface TourGuideProps {
  run: boolean;
  onFinish: () => void;
}

const steps: Step[] = [
  {
    target: "body",
    placement: "center",
    title: "Welcome to AirMind",
    content:
      "AirMind helps you explore historical air quality, forecast pollution levels, identify high-risk stations, and support proactive urban intervention.",
    skipBeacon: true,
  },
  {
    target: "#temporal-replay",
    title: "Historical Replay",
    content:
      "Replay historical air-quality conditions and observe how pollution levels changed across monitoring stations over time.",
    placement: "bottom",
    skipBeacon: true,
  },
  {
    target: "#forecast-summary",
    title: "Forecast Intelligence",
    content:
      "Review AI-generated PM2.5 forecasts and identify potential pollution events before they occur.",
    placement: "bottom",
    skipBeacon: true,
  },
  {
    target: "#air-quality-map",
    title: "Interactive Pollution Map",
    content:
      "Explore station-level pollution geographically and quickly identify affected areas across Chennai.",
    placement: "top",
    skipBeacon: true,
  },
  {
    target: "#hotspot-priority",
    title: "Hotspot Priority",
    content:
      "View the monitoring stations that currently require the highest priority and attention.",
    placement: "top",
    skipBeacon: true,
  },
  {
    target: "#forecast-intelligence",
    title: "Forecast Intelligence",
    content:
      "AirMind converts complex readings and forecasts into a concise operational summary with risks, priorities, and recommended actions.",
    placement: "bottom",
    skipBeacon: true,
  },
  {
    target: "body",
    placement: "center",
    title: "You’re Ready",
    content:
      "You can now explore historical trends, examine forecasts, compare stations, and use the AI brief to support faster decisions.",
    skipBeacon: true,
  },
];

const tourStyles: Partial<Styles> = {
  tooltip: {
    borderRadius: 18,
    padding: 20,
    boxShadow: "0 20px 60px rgba(22, 50, 79, 0.18)",
  },
  tooltipTitle: {
    fontSize: 18,
    fontWeight: 700,
    marginBottom: 10,
  },
  tooltipContent: {
    fontSize: 14,
    lineHeight: 1.65,
    color: "#617A97",
    padding: "4px 0 16px",
  },
  buttonPrimary: {
    backgroundColor: "#4DA3FF",
    borderRadius: 10,
    fontSize: 13,
    fontWeight: 600,
    padding: "10px 16px",
  },
  buttonBack: {
    color: "#617A97",
    fontSize: 13,
    marginRight: 10,
  },
  buttonSkip: {
    color: "#91A4BA",
    fontSize: 13,
  },
};

export default function TourGuide({
  run,
  onFinish,
}: TourGuideProps) {
  const handleEvent = (data: EventData) => {
    if (
      data.status === STATUS.FINISHED ||
      data.status === STATUS.SKIPPED
    ) {
      onFinish();
    }
  };

  return (
    <Joyride
      steps={steps}
      run={run}
      continuous
      onEvent={handleEvent}
      styles={tourStyles}
      options={{
        arrowColor: "#FFFFFF",
        backgroundColor: "#FFFFFF",
        overlayColor: "rgba(16, 42, 67, 0.45)",
        primaryColor: "#4DA3FF",
        textColor: "#16324F",
        width: 390,
        zIndex: 10000,
        showProgress: true,
        skipBeacon: true,
        skipScroll: false,
        blockTargetInteraction: true,
        spotlightRadius: 18,
        buttons: ["back", "close", "primary", "skip"],
      }}
      locale={{
        back: "Back",
        close: "Close",
        last: "Explore AirMind",
        next: "Next",
        skip: "Skip tour",
      }}
    />
  );
}