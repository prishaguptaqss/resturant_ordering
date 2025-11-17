import { View, Text, StyleSheet, ActivityIndicator, TouchableOpacity, Animated } from "react-native";
import { useEffect, useState, useRef } from "react";
import { MicButton } from "../components/MicButton";
import { useRecorder } from "../hooks/useRecorder";
import { Link } from "expo-router";

export default function OrderScreen() {
  const { recording, seconds, toggle, order, isProcessing, transcription, clearOrder } = useRecorder();
  const [processedOrderId, setProcessedOrderId] = useState<string | null>(null);
  const [showOrderCard, setShowOrderCard] = useState(false);
  const [showSuccessCard, setShowSuccessCard] = useState(false);
  const [currentOrder, setCurrentOrder] = useState<any>(null);
  const slideAnim = useRef(new Animated.Value(-400)).current;
  const fadeAnim = useRef(new Animated.Value(0)).current;
  const successSlideAnim = useRef(new Animated.Value(-400)).current;
  const successFadeAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    if (order && order.original_text !== processedOrderId) {
      setProcessedOrderId(order.original_text);
      setCurrentOrder(order);
      setShowOrderCard(true);

      // Slide in and fade in animation
      Animated.parallel([
        Animated.spring(slideAnim, {
          toValue: 0,
          useNativeDriver: true,
          tension: 50,
          friction: 8,
        }),
        Animated.timing(fadeAnim, {
          toValue: 1,
          duration: 300,
          useNativeDriver: true,
        }),
      ]).start();
    }
  }, [order]);

  const hideOrderCard = () => {
    Animated.parallel([
      Animated.timing(slideAnim, {
        toValue: -400,
        duration: 300,
        useNativeDriver: true,
      }),
      Animated.timing(fadeAnim, {
        toValue: 0,
        duration: 300,
        useNativeDriver: true,
      }),
    ]).start(() => {
      setShowOrderCard(false);
      setCurrentOrder(null);
      if (clearOrder) clearOrder();
    });
  };

  const handleConfirmOrder = () => {
    // Hide order card first
    hideOrderCard();
    
    // Show success card after a short delay
    setTimeout(() => {
      setShowSuccessCard(true);
      Animated.parallel([
        Animated.spring(successSlideAnim, {
          toValue: 0,
          useNativeDriver: true,
          tension: 50,
          friction: 8,
        }),
        Animated.timing(successFadeAnim, {
          toValue: 1,
          duration: 300,
          useNativeDriver: true,
        }),
      ]).start();
    }, 400);
  };

  const handleSuccessOkay = () => {
    Animated.parallel([
      Animated.timing(successSlideAnim, {
        toValue: -400,
        duration: 300,
        useNativeDriver: true,
      }),
      Animated.timing(successFadeAnim, {
        toValue: 0,
        duration: 300,
        useNativeDriver: true,
      }),
    ]).start(() => {
      setShowSuccessCard(false);
      successSlideAnim.setValue(-400);
      successFadeAnim.setValue(0);
    });
  };

  const handleCancelOrder = () => {
    hideOrderCard();
  };

  // Get status message
  const getStatusMessage = () => {
    if (recording) {
      return "🎤 Recording…";
    }
    if (isProcessing) {
      if (transcription) {
        return `🧠 Processing: "${transcription}"`;
      }
      return "⏳ Transcribing audio…";
    }
    return "Tap mic to start your order";
  };

  // Get status color
  const getStatusColor = () => {
    if (recording) return "#ef4444";
    if (isProcessing) return "#f59e0b";
    return "#aaa";
  };

  return (
    <View style={styles.container}>
      <Link href="/">
        <Text style={styles.backBtn}>← Menu</Text>
      </Link>

      <Text style={styles.title}>Voice Order</Text>

      {/* Order Confirmation Card - Slides in from top */}
      {showOrderCard && currentOrder && (
        <Animated.View
          style={[
            styles.orderCard,
            {
              transform: [{ translateY: slideAnim }],
              opacity: fadeAnim,
            },
          ]}
        >
          <View style={styles.orderHeader}>
            <Text style={styles.orderTitle}>🍽️ Order Ready</Text>
            <TouchableOpacity onPress={handleCancelOrder} style={styles.closeButton}>
              <Text style={styles.closeButtonText}>✕</Text>
            </TouchableOpacity>
          </View>

          <View style={styles.orderBody}>
            <Text style={styles.orderLabel}>You ordered:</Text>
            {currentOrder.items && currentOrder.items.length > 0 ? (
              currentOrder.items.map((item: any, index: number) => (
                <View key={index} style={styles.orderItem}>
                  <Text style={styles.itemName}>
                    {item.quantity}x {item.name}
                  </Text>
                  <Text style={styles.itemPrice}>₹{item.total_price}</Text>
                </View>
              ))
            ) : (
              <Text style={styles.noItems}>No items detected</Text>
            )}

            <View style={styles.orderTotal}>
              <Text style={styles.totalLabel}>Total</Text>
              <Text style={styles.totalValue}>₹{currentOrder.summary?.total_value || 0}</Text>
            </View>

            <View style={styles.orderActions}>
              <TouchableOpacity
                style={[styles.actionButton, styles.cancelBtn]}
                onPress={handleCancelOrder}
              >
                <Text style={styles.cancelBtnText}>Cancel</Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={[styles.actionButton, styles.confirmBtn]}
                onPress={handleConfirmOrder}
              >
                <Text style={styles.confirmBtnText}>Confirm Order</Text>
              </TouchableOpacity>
            </View>
          </View>
        </Animated.View>
      )}

      {/* Success Confirmation Card */}
      {showSuccessCard && (
        <Animated.View
          style={[
            styles.successCard,
            {
              transform: [{ translateY: successSlideAnim }],
              opacity: successFadeAnim,
            },
          ]}
        >
          <View style={styles.successIconContainer}>
            <Text style={styles.successIcon}>✓</Text>
          </View>
          <Text style={styles.successTitle}>Order Confirmed!</Text>
          <Text style={styles.successMessage}>
            Your order has been placed successfully. 🎉
          </Text>
          <TouchableOpacity
            style={styles.okayButton}
            onPress={handleSuccessOkay}
          >
            <Text style={styles.okayButtonText}>Okay</Text>
          </TouchableOpacity>
        </Animated.View>
      )}

      {/* Processing Indicator */}
      {isProcessing && (
        <View style={styles.processingContainer}>
          <ActivityIndicator size="large" color="#4ade80" />
          <Text style={styles.processingText}>
            {transcription ? "Parsing your order..." : "Transcribing audio..."}
          </Text>
          {transcription && (
            <Text style={styles.transcriptionText}>"{transcription}"</Text>
          )}
        </View>
      )}

      {/* Mic Button */}
      <MicButton recording={recording} onToggle={toggle} disabled={isProcessing} />

      {/* Timer */}
      <Text style={styles.timer}>
        {String(Math.floor(seconds / 60)).padStart(2, "0")}:
        {String(seconds % 60).padStart(2, "0")}
      </Text>

      {/* Status Hint */}
      <Text style={[styles.hint, { color: getStatusColor() }]}>
        {getStatusMessage()}
      </Text>

      {/* Recording Instructions */}
      {!recording && !isProcessing && !showOrderCard && (
        <View style={styles.instructionsContainer}>
          <Text style={styles.instructionsTitle}>💡 Quick Tips:</Text>
          <Text style={styles.instructionText}>• Hold button for at least 1 second</Text>
          <Text style={styles.instructionText}>• Speak clearly near the microphone</Text>
          <Text style={styles.instructionText}>• Say items like "I want a burger and fries"</Text>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#0b0d10",
    padding: 20,
    paddingTop: 60,
  },
  backBtn: {
    color: "#4ade80",
    fontSize: 14,
    marginBottom: 20,
  },
  title: {
    color: "white",
    fontSize: 30,
    fontWeight: "700",
    marginBottom: 40,
    textAlign: "center",
  },
  // Order Confirmation Card Styles
  orderCard: {
    position: "absolute",
    top: 120,
    left: 20,
    right: 20,
    backgroundColor: "#1a1d23",
    borderRadius: 16,
    borderWidth: 2,
    borderColor: "#4ade80",
    shadowColor: "#4ade80",
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
    zIndex: 1000,
  },
  orderHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: "#2a2d35",
  },
  orderTitle: {
    color: "#4ade80",
    fontSize: 20,
    fontWeight: "700",
  },
  closeButton: {
    width: 28,
    height: 28,
    borderRadius: 14,
    backgroundColor: "#374151",
    justifyContent: "center",
    alignItems: "center",
  },
  closeButtonText: {
    color: "#aaa",
    fontSize: 18,
    fontWeight: "600",
  },
  orderBody: {
    padding: 16,
  },
  orderLabel: {
    color: "#aaa",
    fontSize: 13,
    fontWeight: "600",
    marginBottom: 12,
    textTransform: "uppercase",
  },
  orderItem: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: "#2a2d35",
  },
  itemName: {
    color: "white",
    fontSize: 16,
    fontWeight: "500",
  },
  itemPrice: {
    color: "#4ade80",
    fontSize: 16,
    fontWeight: "600",
  },
  noItems: {
    color: "#aaa",
    fontSize: 14,
    textAlign: "center",
    paddingVertical: 20,
  },
  orderTotal: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingTop: 16,
    marginTop: 8,
  },
  totalLabel: {
    color: "white",
    fontSize: 18,
    fontWeight: "700",
  },
  totalValue: {
    color: "#4ade80",
    fontSize: 24,
    fontWeight: "700",
  },
  orderActions: {
    flexDirection: "row",
    gap: 12,
    marginTop: 20,
  },
  actionButton: {
    flex: 1,
    paddingVertical: 14,
    borderRadius: 10,
    alignItems: "center",
  },
  cancelBtn: {
    backgroundColor: "#374151",
  },
  confirmBtn: {
    backgroundColor: "#4ade80",
  },
  cancelBtnText: {
    color: "#aaa",
    fontSize: 15,
    fontWeight: "600",
  },
  confirmBtnText: {
    color: "#0b0d10",
    fontSize: 15,
    fontWeight: "700",
  },
  // Existing styles
  processingContainer: {
    backgroundColor: "#1a1d23",
    borderRadius: 12,
    padding: 20,
    marginBottom: 30,
    alignItems: "center",
    borderWidth: 1,
    borderColor: "#4ade80",
  },
  processingText: {
    color: "#4ade80",
    fontSize: 16,
    fontWeight: "600",
    marginTop: 15,
    textAlign: "center",
  },
  transcriptionText: {
    color: "#aaa",
    fontSize: 14,
    marginTop: 10,
    textAlign: "center",
    fontStyle: "italic",
  },
  timer: {
    color: "white",
    fontSize: 40,
    marginTop: 30,
    textAlign: "center",
    fontWeight: "300",
  },
  hint: {
    textAlign: "center",
    marginTop: 10,
    fontSize: 16,
    fontWeight: "500",
  },
  instructionsContainer: {
    marginTop: 40,
    backgroundColor: "#1a1d23",
    borderRadius: 12,
    padding: 20,
    borderLeftWidth: 4,
    borderLeftColor: "#4ade80",
  },
  instructionsTitle: {
    color: "#4ade80",
    fontSize: 16,
    fontWeight: "700",
    marginBottom: 12,
  },
  instructionText: {
    color: "#aaa",
    fontSize: 14,
    marginBottom: 8,
    paddingLeft: 10,
  },
  // Success Card Styles
  successCard: {
    position: "absolute",
    top: 180,
    left: 20,
    right: 20,
    backgroundColor: "#1a1d23",
    borderRadius: 16,
    borderWidth: 2,
    borderColor: "#4ade80",
    padding: 32,
    alignItems: "center",
    shadowColor: "#4ade80",
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
    zIndex: 1001,
  },
  successIconContainer: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: "#4ade80",
    justifyContent: "center",
    alignItems: "center",
    marginBottom: 20,
  },
  successIcon: {
    color: "#0b0d10",
    fontSize: 48,
    fontWeight: "700",
  },
  successTitle: {
    color: "#4ade80",
    fontSize: 24,
    fontWeight: "700",
    marginBottom: 12,
    textAlign: "center",
  },
  successMessage: {
    color: "white",
    fontSize: 16,
    textAlign: "center",
    marginBottom: 24,
    lineHeight: 24,
  },
  okayButton: {
    backgroundColor: "#4ade80",
    paddingVertical: 14,
    paddingHorizontal: 48,
    borderRadius: 10,
    minWidth: 120,
  },
  okayButtonText: {
    color: "#0b0d10",
    fontSize: 16,
    fontWeight: "700",
    textAlign: "center",
  },
});