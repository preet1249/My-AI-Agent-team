import { View, Text, StyleSheet, ScrollView, TextInput, TouchableOpacity, KeyboardAvoidingView, Platform } from 'react-native'
import { SafeAreaView } from 'react-native-safe-area-context'
import { useState } from 'react'
import { Send, Sparkles, Paperclip, AtSign } from 'lucide-react-native'

export default function ChatScreen() {
  const [message, setMessage] = useState('')
  const [messages, setMessages] = useState<any[]>([])

  const sendMessage = () => {
    if (!message.trim()) return
    setMessages([...messages, { role: 'user', content: message, id: Date.now() }])
    setMessage('')
  }

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <View style={styles.header}>
        <View style={styles.logoContainer}>
          <Sparkles color="#4F9EFF" size={24} />
          <Text style={styles.headerTitle}>AI Agent Team</Text>
        </View>
      </View>

      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.chatContainer}
        keyboardVerticalOffset={100}
      >
        {messages.length === 0 ? (
          <View style={styles.welcomeContainer}>
            <View style={styles.welcomeIconContainer}>
              <Sparkles color="#4F9EFF" size={48} />
            </View>
            <Text style={styles.welcomeTitle}>Hello, Preet</Text>
            <Text style={styles.welcomeSubtitle}>How can I help you today?</Text>

            <View style={styles.quickActions}>
              {[
                { icon: '📊', label: 'Analyze Trends' },
                { icon: '🎯', label: 'Generate Leads' },
                { icon: '📧', label: 'Create Campaign' },
                { icon: '💰', label: 'Budget Planning' },
              ].map((action, index) => (
                <TouchableOpacity key={index} style={styles.quickActionButton}>
                  <Text style={styles.quickActionIcon}>{action.icon}</Text>
                  <Text style={styles.quickActionLabel}>{action.label}</Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>
        ) : (
          <ScrollView style={styles.messagesContainer}>
            {messages.map((msg) => (
              <View key={msg.id} style={styles.messageWrapper}>
                <View style={[
                  styles.messageBubble,
                  msg.role === 'user' ? styles.userBubble : styles.assistantBubble
                ]}>
                  <Text style={[
                    styles.messageText,
                    msg.role === 'user' && styles.userMessageText
                  ]}>
                    {msg.content}
                  </Text>
                </View>
              </View>
            ))}
          </ScrollView>
        )}

        <View style={styles.inputContainer}>
          <View style={styles.inputWrapper}>
            <TouchableOpacity style={styles.iconButton}>
              <Paperclip color="#707070" size={20} />
            </TouchableOpacity>
            <TouchableOpacity style={styles.iconButton}>
              <AtSign color="#707070" size={20} />
            </TouchableOpacity>
            <TextInput
              style={styles.input}
              placeholder="Ask AI Agent Team..."
              placeholderTextColor="#707070"
              value={message}
              onChangeText={setMessage}
              multiline
              maxLength={1000}
            />
            <TouchableOpacity
              style={styles.sendButton}
              onPress={sendMessage}
              disabled={!message.trim()}
            >
              <Send color={message.trim() ? '#FFFFFF' : '#707070'} size={20} />
            </TouchableOpacity>
          </View>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0F0F0F',
  },
  header: {
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#2D2D2D',
  },
  logoContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  headerTitle: {
    fontSize: 18,
    fontFamily: 'Poppins-SemiBold',
    color: '#E8E8E8',
  },
  chatContainer: {
    flex: 1,
  },
  welcomeContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 24,
  },
  welcomeIconContainer: {
    width: 80,
    height: 80,
    borderRadius: 12,
    backgroundColor: '#1A1A1A',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 24,
  },
  welcomeTitle: {
    fontSize: 32,
    fontFamily: 'Poppins-Bold',
    color: '#4F9EFF',
    marginBottom: 8,
  },
  welcomeSubtitle: {
    fontSize: 16,
    fontFamily: 'Poppins-Regular',
    color: '#A0A0A0',
    marginBottom: 32,
  },
  quickActions: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
    justifyContent: 'center',
  },
  quickActionButton: {
    width: '45%',
    backgroundColor: '#1A1A1A',
    borderWidth: 1,
    borderColor: '#2D2D2D',
    borderRadius: 10,
    padding: 16,
    alignItems: 'center',
  },
  quickActionIcon: {
    fontSize: 32,
    marginBottom: 8,
  },
  quickActionLabel: {
    fontSize: 12,
    fontFamily: 'Poppins-Medium',
    color: '#E8E8E8',
    textAlign: 'center',
  },
  messagesContainer: {
    flex: 1,
    padding: 16,
  },
  messageWrapper: {
    marginBottom: 16,
  },
  messageBubble: {
    padding: 12,
    borderRadius: 10,
    maxWidth: '80%',
  },
  userBubble: {
    alignSelf: 'flex-end',
    backgroundColor: '#4F9EFF',
  },
  assistantBubble: {
    alignSelf: 'flex-start',
    backgroundColor: '#1A1A1A',
    borderWidth: 1,
    borderColor: '#2D2D2D',
  },
  messageText: {
    fontSize: 14,
    fontFamily: 'Poppins-Regular',
    color: '#E8E8E8',
    lineHeight: 20,
  },
  userMessageText: {
    color: '#FFFFFF',
  },
  inputContainer: {
    padding: 16,
    borderTopWidth: 1,
    borderTopColor: '#2D2D2D',
    backgroundColor: '#0F0F0F',
  },
  inputWrapper: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#1A1A1A',
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#2D2D2D',
    paddingHorizontal: 8,
    paddingVertical: 8,
  },
  iconButton: {
    padding: 8,
  },
  input: {
    flex: 1,
    fontSize: 14,
    fontFamily: 'Poppins-Regular',
    color: '#E8E8E8',
    paddingHorizontal: 8,
    paddingVertical: 8,
    maxHeight: 100,
  },
  sendButton: {
    width: 40,
    height: 40,
    borderRadius: 10,
    backgroundColor: '#4F9EFF',
    justifyContent: 'center',
    alignItems: 'center',
  },
})
