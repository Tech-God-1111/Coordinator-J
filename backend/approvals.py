class ApprovalGate:
    """Require explicit approval before a tool changes state."""

    def __init__(self):
        self._pending = {}

    def request(self, approval):
        self._pending[approval.approval_id] = approval
        return approval

    def decide(self, approval_id, approved):
        approval = self._pending.pop(approval_id, None)

        if approval is None:
            return False, "Approval request not found or already used."

        if not approved:
            return False, "Action denied by user."

        return True, "Approval granted for this action only."